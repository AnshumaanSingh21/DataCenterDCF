import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import traceback

# ── RAG feature flag ──────────────────────────────────────────────────────────
# Set True to enrich defaults with market-extracted values from the knowledge base.
# Set False to use validated baseline defaults only.
USE_RAG = True

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


# ── RAG assumption cache (per server session, keyed by location+facility_type) ─
# Avoids calling Gemini on every "Run Model" click for the same market.
_rag_cache: dict = {}

CONFIDENCE_THRESHOLD = 0.5

def _get_rag_assumptions(location: str, facility_type: str, total_racks: int, kw_per_rack: float) -> dict:
    """
    Run market_agent once per market per server session.
    Returns {assumption_name: value} for confident extractions only.
    Falls back to empty dict on any failure — defaults take over.
    """
    key = (location, facility_type, total_racks, kw_per_rack)
    if key in _rag_cache:
        return _rag_cache[key]
    try:
        results = market_agent(location, facility_type, total_racks=total_racks, kw_per_rack=kw_per_rack)
        out = {
            name: entry["value"]
            for name, entry in results.items()
            if entry.get("value") is not None
            and entry.get("confidence", 0) >= CONFIDENCE_THRESHOLD
        }
        print(f"[RAG] Extracted {len(out)} assumptions for {location}/{facility_type} ({total_racks} racks): {out}")
    except Exception as e:
        print(f"[RAG] Failed for {location}/{facility_type}: {e}")
        out = {}
    _rag_cache[key] = out
    return out


# ── Response helpers ──────────────────────────────────────────────────────────

def _fmt(v):
    if v is None:
        return None
    return round(float(v), 4)

def _row(lst):
    return [_fmt(x) for x in lst]


# ── Pipeline runner ───────────────────────────────────────────────────────────

def run_pipeline(req: RunRequest):
    ui = {
        "total_racks":       req.total_racks,
        "location":          req.location,
        "facility_type":     req.facility_type,
        "start_year":        req.start_year,
        "projection_years":  req.projection_years,
        "deployment_schedule": {0: 300, 3: 300, 6: 400},
    }

    rev_a  = get_default_revenue_assumptions()
    loan_a = get_default_loan_assumptions()
    cap_a  = get_default_capex_assumptions()

    # ── RAG: override defaults with market-extracted values (confidence ≥ 0.5) ─
    # Guardrail: cap each override at ±30% of the baseline default.
    # Prevents unit errors or outlier data points from distorting the model.
    RAG_MAX_DELTA = 0.20

    def _guarded(rag_val, default_val):
        if default_val == 0:
            return rag_val
        lo = default_val * (1 - RAG_MAX_DELTA)
        hi = default_val * (1 + RAG_MAX_DELTA)
        clamped = max(lo, min(hi, rag_val))
        if clamped != rag_val:
            print(f"[RAG] Clamped {rag_val:.6f} -> {clamped:.6f} (+-20% of default {default_val:.6f})")
        return clamped

    _kw = req.kw_per_rack if req.kw_per_rack is not None else rev_a.get("kw_per_rack", 4.5)
    if USE_RAG:
        rag = _get_rag_assumptions(req.location, req.facility_type, req.total_racks, _kw)
        _rev_map = {
            "rack_price_per_rack_crore":    ("rack_price_per_rack_crore", "rack_mrc_crore"),
            "utility_tariff_rs_per_kwh":    ("utility_tariff_rs_per_kwh",),
            "power_markup_rs_per_kwh":      ("power_markup_rs_per_kwh",),
            "otc_price_per_new_rack_crore": ("otc_price_per_new_rack_crore", "otc_fee_crore"),
            "rack_price_escalation":        ("rack_price_escalation", "rack_mrc_escalation"),
            "power_tariff_escalation":      ("power_tariff_escalation",),
        }
        for rag_key, rev_keys in _rev_map.items():
            if rag_key in rag:
                for k in rev_keys:
                    rev_a[k] = _guarded(rag[rag_key], rev_a[k])

        # CapEx overrides: schema is Cr/MW, engine uses Cr/rack
        # convert: cr_per_rack = cr_per_mw * kw_per_rack / 1000
        _mw_to_rack = _kw / 1000
        _cap_map = {
            "civil_capex_cr_per_mw":       "civil_cost_per_rack",
            "electrical_capex_cr_per_mw":  "electrical_cost_per_rack",
            "mechanical_capex_cr_per_mw":  "mechanical_cost_per_rack",
            "it_hardware_cr_per_rack":     "it_hardware_cost_per_rack",
            "network_capex_cr_per_rack":   "network_cost_per_rack",
        }
        for rag_key, cap_key in _cap_map.items():
            if rag_key in rag and cap_key in cap_a:
                val = rag[rag_key]
                if rag_key.endswith("_per_mw"):
                    val = val * _mw_to_rack
                cap_a[cap_key] = _guarded(val, cap_a[cap_key])

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

    rev  = compute_revenue(ui, rev_a)
    cap  = compute_capex(ui, cap_a)
    opx  = compute_opex(rev, cap, opx_a)
    dep  = compute_depreciation(cap, dep_a)
    loan = compute_loan(cap, loan_a)
    tax  = compute_tax(opx, dep, loan, tax_a)
    wc   = compute_working_capital(rev, wc_a)
    cf   = compute_cashflow(opx, cap, dep, loan, tax, wc, val_a)

    return rev, cap, opx, dep, loan, tax, wc, cf


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/defaults")
def get_defaults():
    la = get_default_loan_assumptions()
    ra = get_default_revenue_assumptions()
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
        "kw_per_rack":       ra.get("kw_per_rack", 4.5),
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
        generate(path)
    except Exception as exc:
        print(f"[Excel] generation failed: {exc}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {exc}")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="DataCenter_DCF_Model.xlsx",
    )
