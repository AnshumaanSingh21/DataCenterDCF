# Handover — Data-Centre DCF Modelling Platform

A production financial-modelling platform that turns a short project brief into a full
discounted-cash-flow (DCF) model for a greenfield data centre: three linked financial
statements, a valuation with return metrics, and a formula-driven Excel workbook.

It is a **deterministic 8-engine financial pipeline** with a **thin AI layer** that only
sources market-intelligence inputs (never the financial logic).

- **Backend:** Python / FastAPI
- **Frontend:** Next.js (React) + Tailwind
- **AI:** Google Gemini (assumption sourcing), with a validator + heuristic fallback
- **Market context:** lightweight RAG (sentence-transformers) over a local knowledge base
- **Deployment:** backend on Render, frontend on Vercel

---

## Read this first — two things to know

1. **`main` is the live branch.** The Render service builds from **`main`** (confirmed in the
   Render dashboard) — the tested, current model. One cosmetic wrinkle: `render.yaml` still
   declares `branch: v2`, which is **stale and ignored** (the dashboard setting wins). Update
   that line to `main` or leave it. The `v2` branch is an old subset of `main` (28 commits
   behind, nothing unique) and is **safe to delete** — it affects nothing live.

2. **`projection_years` means OPERATING years.** The engine adds **+1 construction year**
   internally (year 0). So "10" → 1 build year + 10 operating years = 11 total periods.
   This convention is applied in `src/api/main.py::_build_inputs` and mirrored in the tests
   and the Excel generator. Don't double-count it.

---

## Table of contents
1. [Repository layout](#repository-layout)
2. [Architecture & data flow](#architecture--data-flow)
3. [The financial engine](#the-financial-engine)
4. [The AI assumption layer](#the-ai-assumption-layer)
5. [Assumptions — the knobs](#assumptions--the-knobs)
6. [The Excel generator](#the-excel-generator-and-parity)
7. [How to run locally](#how-to-run-locally)
8. [Configuration & secrets](#configuration--secrets)
9. [Deployment](#deployment)
10. [Testing](#testing)
11. [Conventions & gotchas](#conventions--gotchas)
12. [Common tasks](#common-tasks)
13. [Current state & open items](#current-state--open-items)
14. [Do NOT commit](#do-not-commit)

---

## Repository layout

```
DataCenterDCF/
├── assumptions/                 # DEFAULT MODEL INPUTS — the knobs (one file per engine)
│   ├── revenue_defaults.py      #   get_default_revenue_assumptions()
│   ├── capex_defaults.py        #   civil/electrical/mechanical unit costs, phasing, land
│   ├── opex_defaults.py         #   power, manpower, AMC rates, escalations, warranty
│   ├── depreciation_defaults.py #   useful lives (SLM)
│   ├── loan_defaults.py         #   debt %, interest, moratorium, tenure
│   ├── tax_defaults.py          #   corporate tax rate
│   ├── working_capital_defaults.py
│   └── valuation_defaults.py    #   cost of equity (CAPM-derived), terminal growth, method
│
├── src/
│   ├── api/main.py              # FastAPI app + endpoints; _build_inputs; heuristic fallback
│   ├── engines/                 # THE MODEL — 8 core engines + sizing engines
│   │   ├── revenue_engine.py        capex_engine.py       opex_engine.py
│   │   ├── depreciation_engine.py   loan_engine.py        tax_engine.py
│   │   ├── working_capital_engine.py  cashflow_engine.py
│   │   └── *_sizing_engine.py   # site / it / network / capex sizing helpers
│   ├── reporting/
│   │   └── excel_generator.py   # builds the ~15-sheet Excel workbook (formula-driven)
│   ├── llm/                     # prompts.py, gemini_provider.py, llm_interface.py
│   ├── extraction/              # validator.py (FIELD_MAP + bounds + cross-checks), schema
│   ├── rag/                     # document_loader.py, vector_store.py (market context)
│   ├── pipeline/                # orchestration helpers (run_cashflow, run_capex_sizing)
│   ├── schemas/                 # master_assumption_map.py
│   ├── registry/ · agents/ · utils/   # supporting modules
│
├── frontend/                    # Next.js app
│   ├── app/(main)/              #   dashboard / assumptions / revenue / capex / pnl / cashflow
│   ├── lib/api.js               #   picks backend URL (local vs Render)
│   └── lib/ModelContext.js      #   holds the current run's results
│
├── test_model_integrity.py      # regression suite — run this first (should be 10/10)
├── requirements.txt             # Python deps
├── Procfile · render.yaml       # backend deploy config
├── outputs/                     # market_context.json cache, generated excel_models/
├── knowledge_base/              # source docs for the RAG market context
└── presentation/deck.html       # capability-report slide deck (WIP)
```

---

## Architecture & data flow

```
  User inputs (location, racks, facility type, horizon)
        │
        ▼
  src/api/main.py :: _build_inputs
        │   • adds the +1 construction year
        │   • enriches market values via the AI layer (or heuristic fallback)
        ▼
  8 engines run in sequence (single direction, single source of truth):
        revenue → capex → opex → depreciation → loan → tax → working_capital → cashflow
        │
        ├──► JSON results  ──► frontend dashboard / tables
        └──► excel_generator.generate(...) ──► formula-driven .xlsx
```

There is **no circular calculation** — each engine consumes the previous outputs and
produces the next. `cashflow_engine` assembles the three statements and the DCF valuation.

The clearest, dependency-free way to see the whole pipeline is
**`test_model_integrity.py::run_model()`** — it wires all eight engines together with
default assumptions and no network. Read that function first.

---

## The financial engine

Order and responsibility:

| # | Engine | Produces |
|---|--------|----------|
| 1 | `revenue_engine` | Colocation, power, cross-connect (interconnection) & setup revenue; occupancy from the lease-up curve |
| 2 | `capex_engine` (+ sizing engines) | Civil / electrical / mechanical / network / IT capex; deployment schedule; meet-me-room capex |
| 3 | `opex_engine` | Power, manpower, housekeeping, AMC/maintenance, insurance, property tax, G&A → EBITDA |
| 4 | `depreciation_engine` | Straight-line depreciation by asset class |
| 5 | `loan_engine` | Debt draw, interest, principal, moratorium, closing balance |
| 6 | `tax_engine` | Corporate tax with loss carry-forward (never negative) |
| 7 | `working_capital_engine` | Receivables/payables movements |
| 8 | `cashflow_engine` | P&L + Cash Flow + Balance Sheet, CFADS/DSCR, DCF valuation (NPV, IRR, MOIC, terminal value) |

Each engine takes `(prior_outputs..., assumptions_dict)` and returns a dict. Assumptions come
from `assumptions/*_defaults.py`, optionally overridden per run.

---

## The AI assumption layer

The AI does **not** run the model. It only fills a small set of market-dependent inputs, and
every value it returns is validated before use.

```
  prompt (src/llm/prompts.py)
        ▼
  Gemini  →  candidate market values
        ▼
  validator (src/extraction/validator.py)
        • FIELD_MAP: which fields the LLM may set
        • bounds:    hard min/max per field
        • cross-checks: e.g. an efficient PUE must come with HIGHER cooling capex
        ▼
  accepted values  →  merged into the assumptions  →  engines
```

- **Fields the LLM sources (only these):** grid tariff, power markup, land cost, PUE,
  interest rate, rack MRC, civil cost/rack, mechanical cost/rack. Everything else is
  hardcoded in `assumptions/`.
- **Fallback:** if the LLM/API key is unavailable, `_heuristic_*` in `main.py` supplies
  sane per-facility/per-city defaults so the platform still runs fully offline.
- **Market context (RAG):** `src/rag/` embeds the `knowledge_base/` docs (sentence-transformers)
  to ground the prompt; results are cached in `outputs/market_context.json` (~90-day cache).

---

## Assumptions — the knobs

**To change model behaviour, edit `assumptions/*_defaults.py`.** These are plain Python
dicts returned by `get_default_*()`. Notable ones:

- `revenue_defaults.py` — lease-up curve, rack MRC, escalations (colo 5% / power 4% /
  cross-connect 5%), cross-connect penetration ramp (1.0→1.5) and MRC, PUE.
- `capex_defaults.py` — per-rack civil/mechanical costs, electrical unit prices
  (UPS/DG/transformer), phase split (40/30/30 at years 0/3/6), meet-me-room cost/rack,
  land cost.
- `opex_defaults.py` — AMC rates (civil 2% / elec 4% / mech 8% / net 8% / soft 12%),
  manpower escalation, `maint_warranty_years` (OEM warranty defers MEP AMC), tariffs.
- `valuation_defaults.py` — `cost_of_equity` (CAPM-derived, documented in-comment),
  `terminal_growth_rate`, `valuation_method` (gordon_growth).

---

## The Excel generator (and parity)

`src/reporting/excel_generator.py` builds a ~15-sheet workbook
(ASMP, SIZE, REV, CAPEX, OPEX, DEPR, DEBT, PNL, TAX, WC, CFS, BS, VAL, DASH, COVER).

**It is formula-driven** — every engine calculation is re-expressed as a *native Excel
formula*, so the downloaded file is a working model an analyst can edit, not a static dump.

**The critical invariant: Excel must match the engine.** The parity tests
(`test_excel_matches_engine_*`) generate the workbook, evaluate its formulas with the
`formulas` library, and assert the headline lines equal the engine.

> If you change an engine formula, you MUST update the corresponding `write_*` function in
> `excel_generator.py`, or the parity tests will fail. This is the #1 source of breakage.

Cross-sheet references use row registries (`AR`, `CAP_R`, `OPX_R`, …) populated in
`_predeclare_rows()` — update those if you add/move rows.

---

## How to run locally

**Prerequisites:** Python 3.13, Node.js 18+ (Next.js 16), a virtualenv.

### Backend (API)
```bash
python -m venv venv
# Windows: venv\Scripts\activate   |   *nix: source venv/bin/activate
pip install -r requirements.txt
# create a .env with GEMINI_API_KEY=... (optional — runs offline without it)
uvicorn src.api.main:app --reload --port 8001
```
API then serves at `http://localhost:8001`. Endpoints:
`GET /api/defaults`, `GET /api/market-values`, `POST /api/run`, `POST /api/download`.

### Frontend
```bash
cd frontend
npm install
# point at the local API:
#   set NEXT_PUBLIC_API_URL=http://localhost:8001  (see frontend/.env.local)
npm run dev
```
Frontend serves at `http://localhost:3000`. `lib/api.js` falls back to the Render URL in
production.

### The model, no server needed
```bash
python test_model_integrity.py     # runs the full pipeline + prints 10/10
```

---

## Configuration & secrets

| Variable | Where | Purpose |
|----------|-------|---------|
| `GEMINI_API_KEY` | `.env` (local) / Render env | Gemini API for assumption sourcing. **Never commit.** Without it, the heuristic fallback runs. |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` / Vercel | Backend URL the frontend calls |
| `SENTENCE_TRANSFORMERS_HOME`, `TRANSFORMERS_CACHE` | Render env | Embedding-model cache paths for the RAG layer |

---

## Deployment

- **Backend → Render** (`render.yaml`): `uvicorn src.api.main:app`, `pip install -r requirements.txt`,
  `autoDeploy: true`. **Builds from branch `main`** (confirmed in the Render dashboard). Note that
  `render.yaml` still declares `branch: v2` — that line is stale/unused; the dashboard setting takes
  precedence. Free tier **cold-starts** after inactivity (first request can take ~30–60s).
- **Frontend → Vercel:** standard Next.js build; set `NEXT_PUBLIC_API_URL` to the Render URL.

Note: the live app runs the **LLM-enriched** path, so its numbers differ slightly from the
default-assumptions run in the tests (the tests use flat defaults; the app sources
city-specific market values).

---

## Testing

```bash
python test_model_integrity.py          # or: pytest test_model_integrity.py -q
```
The suite (10 tests) locks in:
- Balance sheet reconciles across base + all scenarios and horizons (5/10/15/20 yrs)
- Occupancy never exceeds deployed capacity
- Construction-year discipline (year 0 has zero revenue/opex/depreciation)
- Base-case headline metrics within tolerance (regression guard)
- DSCR profile shape
- Excel generates for all scenarios **and** matches the engine (parity)

`test_excel_matches_engine_*` needs the `formulas` package; it self-skips if absent.

---

## Conventions & gotchas

- **`projection_years` = operating years; +1 construction added internally.** (See top.)
- **Excel ↔ engine parity is enforced** — change a formula in one place, change it in both.
- **The AI only sets the `FIELD_MAP` fields** — everything else lives in `assumptions/`.
- **Values that read from the run vs hardcoded:** the Excel ASMP sheet reads most sourced
  values from the run's assumption dicts (so parity holds for non-default runs); a few
  display literals exist — check `write_asmp` if a non-default run looks off.
- **`.pyc` files and `outputs/market_context.json` show as modified constantly** — that's
  noise; don't commit them.
- **Cost of equity, terminal value, and cross-connect pricing are deliberately hardcoded /
  derived** (documented in-comment) — they are not LLM-sourced by design.

---

## Common tasks

**Change a model assumption** → edit the relevant `assumptions/*_defaults.py`, then run
`test_model_integrity.py`. If it shifts the base case, update the baseline in
`test_base_case_metrics_within_tolerance`.

**Add / adjust a market field the AI sources** → add it to the prompt (`src/llm/prompts.py`),
to `FIELD_MAP` + bounds (`src/extraction/validator.py`), and read it in the engine. Add a
heuristic fallback in `main.py`.

**Change an engine formula** → update the engine, then the matching `write_*` in
`excel_generator.py`, then run the parity tests.

**Add a city** → extend the per-city tables in `src/llm/prompts.py` (`_CITY_DISCOM`,
`_CITY_MRC_RANGE`) and `LOCATION_LAND_COST` in `capex_defaults.py`.

**Regenerate the Excel manually** → call `excel_generator.generate("out.xlsx")` (uses
defaults) or pass an `override` dict.

---

## Current state & open items

- **Branch:** `main` is the source of truth for development; latest work includes
  cross-connect revenue + meet-me-room capex, CAPM cost of equity, Gordon-growth terminal
  value, benchmarked cooling/electrical/power costs, OEM-warranty AMC deferral, and
  differentiated escalations.
- **Tests:** 10/10 passing on `main`.
- **Open / parked (by design, not bugs):**
  - Optional cleanup: delete the stale `v2` branch, and change `render.yaml`'s `branch: v2`
    line to `main` for accuracy (currently ignored — the dashboard builds `main`).
  - Terminal value assumes a long-hold (Gordon growth) — short (<~10yr) horizons understate
    value; constrain the horizon or add a two-stage TV if short-hold exits are needed.
  - PUE is a single design value (not year-varying) — standard simplification.
  - `presentation/deck.html` — capability report deck, screenshots not yet embedded.

---

## Do NOT commit

- `.env` / `GEMINI_API_KEY` (secrets)
- `outputs/market_context.json` (market cache — churns every run)
- `**/__pycache__/`, `*.pyc` (build artifacts)
- `venv/`, `node_modules/`
- Internal working docs: `PARTNER_BRIEF.md`, `design.md`, `CROSS_CONNECT_MODEL.md`,
  `knowledge_base/` scraped content

---

*For a plain-language overview of the model's methodology and design decisions, see the
capability deck in `presentation/deck.html`.*
