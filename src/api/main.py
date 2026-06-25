import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import traceback

# ── Market intelligence feature flag ─────────────────────────────────────────
# Set True to enrich defaults with LLM-sourced market values (cached 90 days).
# Set False to use validated baseline defaults only.
USE_MARKET_INTELLIGENCE = True

from assumptions.revenue_defaults import get_default_revenue_assumptions
from src.agents.market_agent import market_agent
from assumptions.capex_defaults import get_default_capex_assumptions
from assumptions.opex_defaults import get_default_opex_assumptions
from assumptions.depreciation_defaults import get_default_depreciation_assumptions
from assumptions.loan_defaults import get_default_loan_assumptions
from assumptions.tax_defaults import get_default_tax_assumptions
from assumptions.working_capital_defaults import get_default_working_capital_assumptions
from assumptions.valuation_defaults import get_default_valuation_assumptions

from src.engines.revenue_engine import compute_revenue
from src.engines.capex_engine import compute_capex
from src.engines.opex_engine import compute_opex
from src.engines.depreciation_engine import compute_depreciation
from src.engines.loan_engine import compute_loan
from src.engines.tax_engine import compute_tax
from src.engines.working_capital_engine import compute_working_capital
from src.engines.cashflow_engine import compute_cashflow
from src.reporting.excel_generator import generate
from src.llm.prompts import _CITY_MRC_RANGE, _FACILITY_MRC_MULTIPLIER, _CITY_DISCOM
from assumptions.capex_defaults import LOCATION_LAND_COST

EXCEL_OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "excel_models", "dcf_model.xlsx")

app = FastAPI(title="DataCenter DCF API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request schema ────────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    total_racks:       int            = Field(1000,  ge=1)
    location:          str            = "Mumbai"
    facility_type:     str            = "retail_colo"
    start_year:        int            = Field(2026,  ge=2020)
    projection_years:  int            = Field(10,    ge=5, le=20)
    pue:               float          = Field(1.6,   ge=1.0, le=3.0)
    debt_pct:          float          = Field(0.50,  ge=0.0, le=1.0)
    moratorium_years:  int            = Field(2,     ge=0, le=5)
    interest_rate:     float          = Field(0.10,  ge=0.0, le=0.30)
    # Revenue fields are Optional — if None, RAG/defaults flow through unmodified
    rack_mrc_crore:    Optional[float] = Field(None, ge=0.0)
    util_tariff:       Optional[float] = Field(None, ge=0.0)
    power_markup:      Optional[float] = Field(None, ge=0.0)
    kw_per_rack:       Optional[float] = Field(None, ge=1.0)


# Location-label aliases (frontend label -> anchor-table key)
_LOC_ALIAS       = {"Delhi": "Delhi NCR"}
_FACILITY_PUE    = {"retail_colo": 1.6, "wholesale": 1.55, "ai_hpc": 1.4, "hyperscale": 1.55}
_FACILITY_MARKUP = {"retail_colo": 1.5, "wholesale": 0.75, "ai_hpc": 1.5, "hyperscale": 0.75}


def _band_mid(band: str, default: float = 8.5) -> float:
    """Midpoint of a tariff band string like '8.5–9.5' (handles en/em dashes)."""
    try:
        parts = band.replace("–", "-").replace("—", "-").split("-")
        return round((float(parts[0]) + float(parts[1])) / 2, 2)
    except Exception:
        return default


def _heuristic_market_overrides(location: str, facility_type: str, kw_per_rack: float) -> dict:
    """Location/facility-aware fallback built from the SAME anchor tables the
    LLM prompt uses. Guarantees values vary by location/facility even when the
    LLM is unavailable (quota exhausted, no API key, offline)."""
    loc        = _LOC_ALIAS.get(location, location)
    lo, hi     = _CITY_MRC_RANGE.get(loc, (30_000, 1_50_000))
    mult       = _FACILITY_MRC_MULTIPLIER.get(facility_type, 1.0)
    rack_crore = round((lo + hi) / 2 * mult / 1e7, 6)
    tariff     = _band_mid(_CITY_DISCOM.get(loc, (None, None, None, "8.5-9.5"))[3])
    markup     = _FACILITY_MARKUP.get(facility_type, 1.5)
    pue        = _FACILITY_PUE.get(facility_type, 1.6)
    land       = LOCATION_LAND_COST.get(loc, 5000)
    interest   = 0.105
    return {
        "rev_overrides": {
            "rack_mrc_crore":              rack_crore,
            "rack_price_per_rack_crore":   rack_crore,
            "utility_tariff_rs_per_kwh":   tariff,
            "power_markup_rs_per_kwh":     markup,
            "tenant_power_rate_rs_per_kwh": round(tariff + markup, 2),
            "pue":                         pue,
        },
        "capex_overrides": {"land_cost_per_sqft_rs": land},
        "loan_overrides":  {"interest_rate": interest, "market_interest_rate": interest},
        "audit": [{
            "llm_field": "_heuristic", "source": "heuristic",
            "llm_reasoning": f"location/facility-aware fallback for {location}/{facility_type} "
                             f"(LLM unavailable) derived from anchor ranges",
        }],
        "from_cache": False,
    }


def _get_market_overrides(location: str, facility_type: str, total_racks: int, kw_per_rack: float) -> dict:
    """
    Fetch validated LLM market overrides via market_agent (90-day cached).
    Returns {"rev_overrides": {...}, "capex_overrides": {...}, "loan_overrides": {...}}.
    If the LLM yields nothing usable (failure or zero accepted fields), falls
    back to a location/facility-aware heuristic so values still vary by city —
    never to flat location-independent defaults.
    """
    try:
        result = market_agent(location, facility_type, total_racks=total_racks, kw_per_rack=kw_per_rack)
        accepted = sum(1 for a in result.get("audit", []) if a.get("source") == "llm")
        if accepted == 0:
            print(f"[Market] {location}/{facility_type}: LLM empty -> heuristic fallback")
            return _heuristic_market_overrides(location, facility_type, kw_per_rack)
        src = "cache" if result.get("from_cache") else "llm"
        age = f" age={result.get('cache_age_days')}d" if result.get("from_cache") else ""
        print(f"[Market] {location}/{facility_type}: {accepted} fields from {src}{age}")
        return result
    except Exception as e:
        print(f"[Market] Failed for {location}/{facility_type}: {e} -> heuristic fallback")
        return _heuristic_market_overrides(location, facility_type, kw_per_rack)


# ── Response helpers ──────────────────────────────────────────────────────────

def _fmt(v):
    if v is None:
        return None
    return round(float(v), 4)

def _row(lst):
    return [_fmt(x) for x in lst]


# ── Pipeline runner ───────────────────────────────────────────────────────────

# Last run's inputs + assumption dicts, captured so /api/download can
# regenerate the Excel to match the dashboard without re-calling the LLM.
_LAST_INPUTS = None


def _build_inputs(req: RunRequest):
    """Build the engine inputs and per-engine assumption dicts from a request,
    applying LLM market overrides then explicit UI overrides. Returns
    (ui, assumptions_by_engine)."""
    ui = {
        "total_racks":       req.total_racks,
        "location":          req.location,
        "facility_type":     req.facility_type,
        "start_year":        req.start_year,
        "projection_years":  req.projection_years,
    }

    rev_a  = get_default_revenue_assumptions()
    loan_a = get_default_loan_assumptions()
    cap_a  = get_default_capex_assumptions()

    # ── Market intelligence: override defaults with validated LLM values ─────────
    # Order of precedence: UI inputs > LLM market values > defaults
    # Unit conversions and bounds validation already done inside market_agent/validator.
    _kw = req.kw_per_rack if req.kw_per_rack is not None else rev_a.get("kw_per_rack", 6.0)
    if USE_MARKET_INTELLIGENCE:
        market = _get_market_overrides(req.location, req.facility_type, req.total_racks, _kw)
        rev_a.update(market.get("rev_overrides",   {}))
        cap_a.update(market.get("capex_overrides", {}))
        loan_a.update(market.get("loan_overrides", {}))

    # ── UI overrides: only apply fields the user explicitly set (not None) ──────
    rev_a["pue"] = req.pue
    if req.kw_per_rack   is not None: rev_a["kw_per_rack"]               = req.kw_per_rack
    if req.rack_mrc_crore is not None:
        rev_a["rack_mrc_crore"]            = req.rack_mrc_crore
        rev_a["rack_price_per_rack_crore"] = req.rack_mrc_crore
    if req.util_tariff   is not None: rev_a["utility_tariff_rs_per_kwh"] = req.util_tariff
    if req.power_markup  is not None: rev_a["power_markup_rs_per_kwh"]   = req.power_markup

    loan_a["debt_pct"]         = req.debt_pct
    loan_a["moratorium_years"] = req.moratorium_years
    loan_a["interest_rate"]    = req.interest_rate

    opx_a  = get_default_opex_assumptions()
    dep_a  = get_default_depreciation_assumptions()
    tax_a  = get_default_tax_assumptions()
    wc_a   = get_default_working_capital_assumptions()
    val_a  = get_default_valuation_assumptions()

    return ui, {
        "rev": rev_a, "cap": cap_a, "opx": opx_a, "dep": dep_a,
        "loan": loan_a, "tax": tax_a, "wc": wc_a, "val": val_a,
    }


def run_pipeline(req: RunRequest):
    global _LAST_INPUTS
    ui, A = _build_inputs(req)

    # Persist this run's inputs + assumptions so /api/download can rebuild
    # the Excel to match the dashboard (the base ui has no deployment_schedule;
    # the Excel derives it from CapEx itself, same single-source rule).
    _LAST_INPUTS = {"ui": ui, **A}

    # CapEx is the single source of truth for deployed capacity.
    # Compute it first, then cap revenue occupancy by what was
    # actually fitted out (you can't lease a rack that isn't built).
    cap  = compute_capex(ui, A["cap"])
    ui   = {**ui, "deployment_schedule": {
        p["year"]: p["racks"] for p in cap["deployment_schedule"]
    }}
    rev  = compute_revenue(ui, A["rev"])
    opx  = compute_opex(rev, cap, A["opx"])
    dep  = compute_depreciation(cap, A["dep"])
    loan = compute_loan(cap, A["loan"])
    tax  = compute_tax(opx, dep, loan, A["tax"])
    wc   = compute_working_capital(rev, A["wc"])
    cf   = compute_cashflow(opx, cap, dep, loan, tax, wc, A["val"])

    return rev, cap, opx, dep, loan, tax, wc, cf


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/defaults")
def get_defaults():
    la = get_default_loan_assumptions()
    ra = get_default_revenue_assumptions()

    # Enrich with LLM market values for default location (cached 90 days)
    kw = ra.get("kw_per_rack", 6.0)
    if USE_MARKET_INTELLIGENCE:
        market = _get_market_overrides("Mumbai", "retail_colo", 1000, kw)
        ra.update(market.get("rev_overrides", {}))
        la.update(market.get("loan_overrides", {}))

    return {
        "total_racks":       1000,
        "location":          "Mumbai",
        "facility_type":     "retail_colo",
        "start_year":        2026,
        "projection_years":  10,
        "pue":               ra["pue"],
        "debt_pct":          la["debt_pct"],
        "moratorium_years":  la["moratorium_years"],
        "interest_rate":     la["interest_rate"],
        "rack_mrc_crore":    ra["rack_mrc_crore"],
        "util_tariff":       ra["utility_tariff_rs_per_kwh"],
        "power_markup":      ra["power_markup_rs_per_kwh"],
        "kw_per_rack":       ra.get("kw_per_rack", 6.0),
    }


@app.get("/api/market-values")
def get_market_values(location: str = "Mumbai", facility_type: str = "retail_colo", kw_per_rack: float = 6.0):
    """Return LLM-sourced market values for a given location and facility type."""
    la = get_default_loan_assumptions()
    ra = get_default_revenue_assumptions()

    if USE_MARKET_INTELLIGENCE:
        market = _get_market_overrides(location, facility_type, 1000, kw_per_rack)
        ra.update(market.get("rev_overrides", {}))
        la.update(market.get("loan_overrides", {}))

    return {
        "pue":           ra["pue"],
        "interest_rate": la["interest_rate"],
        "rack_mrc_crore": ra["rack_mrc_crore"],
        "util_tariff":   ra["utility_tariff_rs_per_kwh"],
        "power_markup":  ra["power_markup_rs_per_kwh"],
        "kw_per_rack":   ra.get("kw_per_rack", kw_per_rack),
    }


@app.post("/api/run")
def run_model(req: RunRequest):
    try:
        rev, cap, opx, dep, loan, tax, wc, cf = run_pipeline(req)
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())

    years       = rev["metadata"]["years"]
    net_rev     = rev["revenue_streams"]["net_revenue"]
    rack_rev    = rev["revenue_streams"].get("recurring_colo_revenue", [0]*len(years))
    pwr_rev     = rev["revenue_streams"].get("power_revenue", [0]*len(years))
    otc_rev     = rev["revenue_streams"].get("otc_setup_revenue", [0]*len(years))

    ebitda      = opx["financials"]["ebitda"]
    ebitda_m    = opx["financials"]["ebitda_margin"]
    total_opx   = opx["financials"]["total_opex"]

    cx_comp     = cap["capex_components"]
    total_cx    = cap["financials"]["total_capex"]
    civil_cx    = cx_comp.get("civil_capex",       [0]*len(years))
    elec_cx     = cx_comp.get("electrical_capex",  [0]*len(years))
    mech_cx     = cx_comp.get("mechanical_capex",  [0]*len(years))
    it_cx       = cx_comp.get("it_hardware_capex", [0]*len(years))
    net_cx      = cx_comp.get("network_capex",     [0]*len(years))

    dep_tot     = dep["financials"]["total_depreciation"]
    interest    = loan["long_term_debt_account"]["interest_expense"]
    principal   = loan["long_term_debt_account"]["principal_repayment"]
    debt_clos   = loan["long_term_debt_account"]["closing_balance"]

    pat         = tax["financials"]["pat"]
    tax_exp     = tax["financials"]["tax"]

    cfads       = cf["cashflows"]["cfads"]
    ds          = cf["cashflows"]["debt_service"]
    dscr_raw    = cf["cashflows"]["dscr"]
    dscr        = [max(x, 0) if x is not None else None for x in dscr_raw]

    iv          = cf["valuation"]
    eq          = cf["equity"]
    cs          = loan["capital_structure"]

    return {
        "years": years,
        "kpis": {
            "project_irr":      _fmt(iv["project_irr"] * 100),
            "equity_irr":       _fmt(iv["equity_irr"] * 100),
            "npv":              _fmt(iv["npv"]),
            "moic":             _fmt(iv["moic"]),
            "wacc":             _fmt(iv["wacc"] * 100),
            "terminal_value":   _fmt(iv["terminal_value"]),
            "total_capex":      _fmt(sum(total_cx)),
            "equity_invested":  _fmt(eq["total_equity_invested"]),
        },
        "revenue": {
            "net_revenue":   _row(net_rev),
            "rack_revenue":  _row(rack_rev),
            "power_revenue": _row(pwr_rev),
            "otc_revenue":   _row(otc_rev),
        },
        "capex": {
            "total_capex":  _row(total_cx),
            "civil":        _row(civil_cx),
            "electrical":   _row(elec_cx),
            "mechanical":   _row(mech_cx),
            "it":           _row(it_cx),
            "network":      _row(net_cx),
        },
        "pnl": {
            "net_revenue":    _row(net_rev),
            "total_opex":     _row(total_opx),
            "ebitda":         _row(ebitda),
            "ebitda_margin":  _row(ebitda_m),
            "depreciation":   _row(dep_tot),
            "interest":       _row(interest),
            "tax":            _row(tax_exp),
            "pat":            _row(pat),
        },
        "cashflow": {
            "cfads":         _row(cfads),
            "interest":      _row(interest),
            "principal":     _row(principal),
            "debt_service":  _row(ds),
            "dscr":          _row(dscr),
            "closing_debt":  _row(debt_clos),
        },
        "excel_ready": True,
    }


@app.get("/api/download")
def download_excel():
    try:
        path = os.path.abspath(EXCEL_OUT)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Rebuild the workbook to match the most recent run; falls back to
        # module defaults if the model hasn't been run yet this session.
        generate(path, override=_LAST_INPUTS)
    except Exception as exc:
        print(f"[Excel] generation failed: {exc}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {exc}")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="DataCenter_DCF_Model.xlsx",
    )
