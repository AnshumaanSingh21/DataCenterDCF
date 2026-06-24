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


def _get_market_overrides(location: str, facility_type: str, total_racks: int, kw_per_rack: float) -> dict:
    """
    Fetch validated LLM market overrides via market_agent (90-day cached).
    Returns {"rev_overrides": {...}, "capex_overrides": {...}, "loan_overrides": {...}}.
    Falls back to empty dicts on any failure — defaults take over.
    """
    try:
        result = market_agent(location, facility_type, total_racks=total_racks, kw_per_rack=kw_per_rack)
        src = "cache" if result.get("from_cache") else "llm"
        age = f" age={result.get('cache_age_days')}d" if result.get("from_cache") else ""
        accepted = sum(1 for a in result.get("audit", []) if a.get("source") == "llm")
        print(f"[Market] {location}/{facility_type}: {accepted} fields from {src}{age}")
        return result
    except Exception as e:
        print(f"[Market] Failed for {location}/{facility_type}: {e}")
        return {"rev_overrides": {}, "capex_overrides": {}, "loan_overrides": {}}


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
        "kw_per_rack":       ra.get("kw_per_rack", 6.0),
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
