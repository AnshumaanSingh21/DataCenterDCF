"""
Model integrity regression tests.

Locks in the correctness work: the 3-statement balance sheet must tie to zero,
the deployment buffer must hold, horizons must be length-safe, and the base-case
headline metrics must stay within tolerance. Runs the engines directly with
defaults (no LLM / no network).

Run:  pytest test_model_integrity.py -q
  or: python test_model_integrity.py
"""
import warnings
warnings.filterwarnings("ignore")

from assumptions.revenue_defaults import get_default_revenue_assumptions
from assumptions.opex_defaults import get_default_opex_assumptions
from assumptions.capex_defaults import get_default_capex_assumptions
from assumptions.depreciation_defaults import get_default_depreciation_assumptions
from assumptions.loan_defaults import get_default_loan_assumptions
from assumptions.tax_defaults import get_default_tax_assumptions
from assumptions.working_capital_defaults import get_default_working_capital_assumptions
from assumptions.valuation_defaults import get_default_valuation_assumptions

from src.engines.revenue_engine import compute_revenue
from src.engines.opex_engine import compute_opex
from src.engines.capex_engine import compute_capex
from src.engines.depreciation_engine import compute_depreciation
from src.engines.loan_engine import compute_loan
from src.engines.tax_engine import compute_tax
from src.engines.working_capital_engine import compute_working_capital
from src.engines.cashflow_engine import compute_cashflow

BASE = {
    "location": "Mumbai", "total_racks": 1000, "facility_type": "retail_colo",
    "projection_years": 10, "start_year": 2026,
}

SCENARIOS = [
    {"location": "Hyderabad", "total_racks": 1500, "facility_type": "wholesale",   "projection_years": 15, "start_year": 2026},
    {"location": "Bangalore", "total_racks": 500,  "facility_type": "retail_colo", "projection_years": 20, "start_year": 2026},
    {"location": "Delhi",     "total_racks": 2000, "facility_type": "ai_hpc",      "projection_years": 12, "start_year": 2026},
]


def run_model(user_inputs):
    """Run the full pipeline with default assumptions (no LLM). CapEx owns the
    deployment schedule; revenue occupancy is capped by it (single source)."""
    cap = compute_capex(user_inputs, get_default_capex_assumptions())
    ui = {**user_inputs, "deployment_schedule": {
        p["year"]: p["racks"] for p in cap["deployment_schedule"]
    }}
    rev = compute_revenue(ui, get_default_revenue_assumptions())
    opx = compute_opex(rev, cap, get_default_opex_assumptions())
    dep = compute_depreciation(cap, get_default_depreciation_assumptions())
    loan = compute_loan(cap, get_default_loan_assumptions())
    tax = compute_tax(opx, dep, loan, get_default_tax_assumptions())
    wc = compute_working_capital(rev, get_default_working_capital_assumptions(), opx)
    cf = compute_cashflow(opx, cap, dep, loan, tax, wc, get_default_valuation_assumptions())
    return dict(rev=rev, cap=cap, opx=opx, dep=dep, loan=loan, tax=tax, wc=wc, cf=cf)


# ── Balance sheet integrity ─────────────────────────────────────────────────

def test_balance_sheet_ties_base():
    cf = run_model(BASE)["cf"]
    for yr, chk in zip(cf["metadata"]["years"], cf["balance_sheet"]["balance_check"]):
        assert abs(chk) < 1e-6, f"balance check {chk} != 0 in {yr}"


def test_balance_sheet_ties_all_scenarios():
    for s in SCENARIOS:
        cf = run_model(s)["cf"]
        for chk in cf["balance_sheet"]["balance_check"]:
            assert abs(chk) < 1e-6, f"balance broke in {s['location']}/{s['facility_type']}"


# ── Capacity coherence (single source of truth) ─────────────────────────────

def test_occupancy_never_exceeds_deployment():
    for s in [BASE] + SCENARIOS:
        out = run_model(s)
        occ = out["rev"]["drivers"]["occupied_racks"]
        rd = out["cap"]["drivers"]["racks_deployed"]
        cum, running = [], 0
        for x in rd:
            running += x
            cum.append(running)
        for i in range(len(occ)):
            assert cum[i] >= occ[i] - 0.01, f"occupancy exceeds deployment in {s['location']}"


# ── Dynamic horizon length-safety ───────────────────────────────────────────

def test_horizons_length_safe():
    for yrs in (5, 10, 15, 20):
        out = run_model({**BASE, "projection_years": yrs})
        assert len(out["cf"]["metadata"]["years"]) == yrs
        assert len(out["rev"]["drivers"]["occupied_racks"]) == yrs
        for chk in out["cf"]["balance_sheet"]["balance_check"]:
            assert abs(chk) < 1e-6


# ── Construction year discipline ────────────────────────────────────────────

def test_construction_year_is_clean():
    out = run_model(BASE)
    # Year 0 (construction): zero revenue, zero opex, zero depreciation
    assert out["rev"]["revenue_streams"]["net_revenue"][0] == 0.0
    assert out["opx"]["financials"]["total_opex"][0] == 0.0
    assert out["dep"]["financials"]["book_depreciation"][0] == 0.0


# ── Base-case headline metrics (regression guard) ───────────────────────────

def test_base_case_metrics_within_tolerance():
    cf = run_model(BASE)["cf"]
    v = cf["valuation"]
    assert abs(v["npv"] - 124.8) < 2.0,                f"NPV drifted: {v['npv']}"
    assert abs(v["project_irr"] - 0.185) < 0.01,       f"Project IRR drifted: {v['project_irr']}"
    assert abs(v["equity_irr"] - 0.216) < 0.01,        f"Equity IRR drifted: {v['equity_irr']}"
    assert abs(cf["equity"]["moic"] - 4.74) < 0.3,     f"MOIC drifted: {cf['equity']['moic']}"


def test_dscr_profile_shape():
    cf = run_model(BASE)["cf"]
    dscr = [d for d in cf["cashflows"]["dscr"] if d is not None]
    # Greenfield shape: ramps up, ends well above covenant
    assert dscr[1] < 0.5            # early lease-up year is weak
    assert dscr[-1] > 2.0           # stabilized years comfortably covered
    # non-construction DSCR should be non-decreasing in the back half
    assert dscr[-1] >= dscr[-3]


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL  {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} passed")
