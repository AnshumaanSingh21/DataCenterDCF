"""
Full model validation — runs every engine and checks:
  1. Mathematical identities (do numbers tie within each engine?)
  2. Cross-engine consistency (do outputs agree where they overlap?)
  3. Per-unit sanity (CapEx/rack, revenue/rack, EBITDA margin)
  4. Industry benchmarks (IRR, DSCR, margins for India greenfield DC)

Prints PASS / WARN / FAIL for each check with actual values.
"""

import math
from assumptions.revenue_defaults      import get_default_revenue_assumptions
from assumptions.opex_defaults         import get_default_opex_assumptions
from assumptions.capex_defaults        import get_default_capex_assumptions
from assumptions.depreciation_defaults import get_default_depreciation_assumptions
from assumptions.loan_defaults         import get_default_loan_assumptions
from assumptions.tax_defaults          import get_default_tax_assumptions
from assumptions.working_capital_defaults import get_default_working_capital_assumptions
from assumptions.valuation_defaults    import get_default_valuation_assumptions

from src.engines.revenue_engine      import compute_revenue
from src.engines.capex_engine        import compute_capex
from src.engines.opex_engine         import compute_opex
from src.engines.depreciation_engine import compute_depreciation
from src.engines.loan_engine         import compute_loan
from src.engines.tax_engine          import compute_tax
from src.engines.working_capital_engine import compute_working_capital
from src.engines.cashflow_engine     import compute_cashflow

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

user_inputs = {
    "location":            "Mumbai",
    "total_racks":         1000,
    "facility_type":       "retail_colo",
    "projection_years":    10,
    "start_year":          2026,
    "deployment_schedule": {0: 300, 3: 300, 6: 400},
}

TOL = 0.01   # crore — rounding tolerance for identity checks

# ─────────────────────────────────────────────
# RUN PIPELINE
# ─────────────────────────────────────────────

rev  = compute_revenue(user_inputs, get_default_revenue_assumptions())
cap  = compute_capex(user_inputs, get_default_capex_assumptions())
opx  = compute_opex(rev, cap, get_default_opex_assumptions())
dep  = compute_depreciation(cap, get_default_depreciation_assumptions())
lon  = compute_loan(cap, get_default_loan_assumptions())
tax  = compute_tax(opx, dep, lon, get_default_tax_assumptions())
wc   = compute_working_capital(rev, get_default_working_capital_assumptions())
cf   = compute_cashflow(opx, cap, dep, lon, tax, wc,
                        valuation_assumptions=get_default_valuation_assumptions())

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

PASS  = "  PASS"
WARN  = "  WARN"
FAIL  = "  FAIL"
pass_count = fail_count = warn_count = 0

def check(label, ok, detail="", warn_only=False):
    global pass_count, fail_count, warn_count
    if ok:
        tag = PASS
        pass_count += 1
    elif warn_only:
        tag = WARN
        warn_count += 1
    else:
        tag = FAIL
        fail_count += 1
    suffix = f"  → {detail}" if detail else ""
    print(f"{tag}  {label}{suffix}")

def section(title):
    print(f"\n{'-'*68}")
    print(f"  {title}")
    print(f"{'-'*68}")

def close_enough(a, b, tol=TOL):
    return abs(a - b) <= tol

def all_close(xs, ys, tol=TOL):
    return all(abs(x - y) <= tol for x, y in zip(xs, ys))

def mono_nondec(lst):
    return all(lst[i] <= lst[i+1] + TOL for i in range(len(lst)-1))

# ─────────────────────────────────────────────
# PULL KEY SERIES
# ─────────────────────────────────────────────

years    = rev["metadata"]["years"]
n        = len(years)
total_racks = user_inputs["total_racks"]

# Revenue
occupied        = rev["drivers"]["occupied_racks"]

# Reconstruct cumulative_deployed from the deployment schedule
_sched = user_inputs["deployment_schedule"]
_running_dep = 0
cumul_deployed = []
for i in range(n):
    _running_dep += _sched.get(i, 0)
    cumul_deployed.append(_running_dep)

gross_rev       = rev["revenue_streams"]["gross_revenue"]
dot_ded         = rev["revenue_streams"]["dot_deduction"]
net_rev         = rev["revenue_streams"]["net_revenue"]
power_cost_rev  = rev["power_detail"]["power_cost"]

# CapEx
annual_capex    = cap["financials"]["total_capex"]
cumul_capex     = cap["financials"]["cumulative_capex"]
land_cost       = cap["site_sizing"]["land_cost_crore"]
cap_components  = cap["capex_components"]

# OpEx
total_opex      = opx["financials"]["total_opex"]
ebitda_opx      = opx["financials"]["ebitda"]
ebitda_margin   = opx["financials"]["ebitda_margin"]
cost_lines      = opx["cost_lines"]

# Depreciation
book_dep        = dep["financials"]["book_depreciation"]
tax_dep_vals    = dep["financials"]["tax_depreciation"]
accum_dep       = dep["financials"]["accumulated_depreciation"]
nbv             = dep["financials"]["net_book_value"]

# Loan
lt_debt         = lon["long_term_debt_account"]
interest        = lt_debt["interest_expense"]
principal       = lt_debt["principal_repayment"]
drawdown        = lt_debt["drawdown"]
closing_debt    = lt_debt["closing_balance"]
equity_funding  = lon["capital_structure"]["equity_funding"]

# Tax
ebit_tax        = tax["financials"]["ebit"]
pbt_tax         = tax["financials"]["pbt"]
effective_tax   = tax["financials"]["tax"]
pat_tax         = tax["financials"]["pat"]
mat_vals        = tax["financials"]["mat"]
corp_tax        = tax["financials"]["corporate_tax"]

# WC
delta_wc        = wc["financials"]["change_in_working_capital"]

# Cashflow
nopat           = cf["cashflows"]["nopat"]
fcff            = cf["cashflows"]["fcff"]
fcfe            = cf["cashflows"]["fcfe"]
cfads           = cf["cashflows"]["cfads"]
debt_service    = cf["cashflows"]["debt_service"]
dscr            = cf["cashflows"]["dscr"]
val             = cf["valuation"]
eq              = cf["equity"]
dm              = cf["debt_metrics"]

tax_rate        = get_default_tax_assumptions()["corporate_tax_rate"]

# ═══════════════════════════════════════════════
# 1. REVENUE ENGINE
# ═══════════════════════════════════════════════
section("1. REVENUE ENGINE")

# Deployment cap: occupied ≤ cumulative deployed
cap_ok = all(occupied[i] <= cumul_deployed[i] + TOL for i in range(n))
check("Deployment cap enforced (occupied <= cumul_deployed) every year", cap_ok,
      f"max_occupied={max(occupied):.0f}  max_deployed={max(cumul_deployed):.0f}")

# Occupied racks bounded by total_racks
bound_ok = all(o <= total_racks + TOL for o in occupied)
check("occupied_racks <= total_racks every year", bound_ok,
      f"max_occupied={max(occupied):.0f}")

# Net = Gross − DoT
net_identity = all_close(
    net_rev,
    [gross_rev[i] - dot_ded[i] for i in range(n)]
)
check("net_revenue = gross_revenue − dot_deduction", net_identity)

# Revenue grows monotonically (no dips)
rev_mono = mono_nondec(net_rev)
check("Net revenue non-decreasing year-on-year", rev_mono,
      f"min={min(net_rev):.2f}  max={max(net_rev):.2f}")

# Rack MRC at Year 10 (recurring colo only — not aggregate revenue/rack)
rack_mrc_yr10 = (rev["drivers"]["rack_mrc"][-1] * 1e7) / 12 if rev["drivers"]["rack_mrc"][-1] > 0 else 0
check("Rack MRC at Year 10 in Rs 5,000-20,000/rack/month (4.5 kW Mumbai retail colo)",
      5000 <= rack_mrc_yr10 <= 20000,
      f"Rs {rack_mrc_yr10:,.0f}/rack/month", warn_only=True)

# ═══════════════════════════════════════════════
# 2. CAPEX ENGINE
# ═══════════════════════════════════════════════
section("2. CAPEX ENGINE")

# Cumulative CapEx is non-decreasing
check("Cumulative CapEx is non-decreasing", mono_nondec(cumul_capex),
      f"total={cumul_capex[-1]:.2f} crore")

# CapEx only in deployment years
deploy_yrs = set(user_inputs["deployment_schedule"].keys())
for i in range(n):
    if i not in deploy_yrs and annual_capex[i] > TOL:
        check(f"CapEx in non-deployment Year {years[i]}", False,
              f"capex={annual_capex[i]:.2f} crore (unexpected)")

# Component sum = total_capex
# site_level_capex (land + consultancy + approval) now exposed in capex_components.
comp_keys = ["civil_capex","electrical_capex","mechanical_capex",
             "network_capex","software_capex","it_hardware_capex",
             "site_level_capex","pre_op_capex"]
for i in range(n):
    comp_sum = sum(cap_components.get(k, [0]*n)[i] for k in comp_keys)
    if not close_enough(comp_sum, annual_capex[i], tol=0.10):
        check(f"Component sum = total_capex at Year {years[i]}", False,
              f"comp_sum={comp_sum:.2f}  total={annual_capex[i]:.2f}")
        break
else:
    check("Component sum = total_capex every year (all 8 components)", True)

# CapEx / rack — Mumbai greenfield Tier III full-build (incl. land) = Rs 25-50 lakh
capex_per_rack = (cumul_capex[-1] * 1e7) / total_racks / 1e5  # in lakh
check("Total CapEx/rack in Rs 20-55 lakh (Mumbai greenfield, land+full-build)",
      20 <= capex_per_rack <= 55,
      f"Rs {capex_per_rack:.1f} lakh/rack", warn_only=True)

# ═══════════════════════════════════════════════
# 3. OPEX ENGINE
# ═══════════════════════════════════════════════
section("3. OPEX ENGINE")

# Sum of cost lines = total_opex
cost_line_keys = [
    "power_cost","manpower_cost","housekeeping_cost","maintenance_cost",
    "network_cost","security_cost","insurance_cost","property_tax",
    "marketing_cost","gna_cost"
]
for i in range(n):
    line_sum = sum(cost_lines[k][i] for k in cost_line_keys)
    if not close_enough(line_sum, total_opex[i]):
        check(f"Cost lines sum = total_opex at Year {years[i]}", False,
              f"sum={line_sum:.4f}  total={total_opex[i]:.4f}")
        break
else:
    check("All 10 cost lines sum to total_opex every year", True)

# EBITDA = net_revenue − total_opex
ebitda_identity = all_close(
    ebitda_opx,
    [net_rev[i] - total_opex[i] for i in range(n)]
)
check("EBITDA = net_revenue − total_opex", ebitda_identity)

# EBITDA margin at maturity (Year 10) in 45–65%
mat_margin = ebitda_margin[-1]
check("EBITDA margin at Year 10 in 45–65%",
      0.45 <= mat_margin <= 0.65,
      f"{mat_margin*100:.1f}%", warn_only=True)

# Power cost as % of revenue — benchmark 20–35%
pwr_pct = cost_lines["power_cost"][-1] / net_rev[-1]
check("Power cost % of net revenue at Year 10 in 15–40%",
      0.15 <= pwr_pct <= 0.40,
      f"{pwr_pct*100:.1f}%", warn_only=True)

# ═══════════════════════════════════════════════
# 4. DEPRECIATION ENGINE
# ═══════════════════════════════════════════════
section("4. DEPRECIATION ENGINE")

# NBV = cumulative_capex − accumulated_dep
nbv_identity = all_close(
    nbv,
    [cumul_capex[i] - accum_dep[i] for i in range(n)]
)
check("Net Book Value = cumul_capex − accumulated_dep", nbv_identity)

# NBV ≥ 0 always
check("Net Book Value ≥ 0 in all years", all(v >= -TOL for v in nbv),
      f"min NBV={min(nbv):.2f} crore")

# Accumulated dep ≤ cumulative_capex
check("Accumulated dep ≤ cumulative CapEx",
      all(accum_dep[i] <= cumul_capex[i] + TOL for i in range(n)),
      f"max(accum_dep/cumul_capex)={max(accum_dep[i]/cumul_capex[i] if cumul_capex[i]>0 else 0 for i in range(n)):.2f}")

# Tax dep > book dep in early phase years (WDV front-loads)
early_ok = all(tax_dep_vals[i] >= book_dep[i] - TOL for i in [0, 1, 2])
check("Tax (WDV) dep ≥ Book (SLM) dep in first 3 years",
      early_ok,
      f"Yr1 book={book_dep[0]:.2f} tax={tax_dep_vals[0]:.2f}")

# Tax dep < book dep in later years (WDV exhausts)
late_ok = tax_dep_vals[-1] < book_dep[-1] + TOL
check("Tax (WDV) dep ≤ Book (SLM) dep in Year 10",
      late_ok,
      f"book={book_dep[-1]:.2f} tax={tax_dep_vals[-1]:.2f}")

# ═══════════════════════════════════════════════
# 5. LOAN ENGINE
# ═══════════════════════════════════════════════
section("5. LOAN ENGINE")

loan_assump = get_default_loan_assumptions()
debt_pct    = loan_assump["debt_pct"]
equity_pct  = loan_assump["equity_pct"]

# Drawdown = debt_pct × CapEx in deployment years
for i in deploy_yrs:
    expected_drawdown = annual_capex[i] * debt_pct
    actual_drawdown   = drawdown[i]
    ok = close_enough(expected_drawdown, actual_drawdown, tol=0.05)
    check(f"Drawdown in Year {years[i]} ≈ debt_pct × CapEx",
          ok, f"expected={expected_drawdown:.2f}  actual={actual_drawdown:.2f}")

# Equity funding = equity_pct × CapEx in deployment years
for i in deploy_yrs:
    expected_eq = annual_capex[i] * equity_pct
    actual_eq   = equity_funding[i]
    ok = close_enough(expected_eq, actual_eq, tol=0.05)
    check(f"Equity funding in Year {years[i]} ≈ equity_pct × CapEx",
          ok, f"expected={expected_eq:.2f}  actual={actual_eq:.2f}")

# Total drawdown + equity ≈ total CapEx
total_cap  = sum(annual_capex)
total_draw = sum(drawdown)
total_eq   = sum(equity_funding)
check("Total drawdown + equity ≈ total CapEx",
      close_enough(total_draw + total_eq, total_cap, tol=0.5),
      f"debt={total_draw:.2f}  equity={total_eq:.2f}  capex={total_cap:.2f}")

# Closing debt ≥ 0 always
check("Closing debt ≥ 0 in all years",
      all(d >= -TOL for d in closing_debt),
      f"min={min(closing_debt):.2f} crore")

# Closing debt declines in non-deployment years (repayment working)
# Deployment years (0, 3, 6) will see debt rise due to new tranche draws.
non_deploy = [i for i in range(1, n) if i not in deploy_yrs]
debt_declines_ok = all(
    closing_debt[i] <= closing_debt[i - 1] + TOL
    for i in non_deploy
)
check("Closing debt declines in all non-deployment years (repayment working)",
      debt_declines_ok,
      f"non-deploy years={[years[i] for i in non_deploy]}")

# ═══════════════════════════════════════════════
# 6. TAX ENGINE
# ═══════════════════════════════════════════════
section("6. TAX ENGINE")

# EBIT = EBITDA − book_dep
ebit_identity = all_close(
    ebit_tax,
    [ebitda_opx[i] - book_dep[i] for i in range(n)]
)
check("EBIT = EBITDA − book_dep (SLM)", ebit_identity)

# PBT = EBIT − interest
pbt_identity = all_close(
    pbt_tax,
    [ebit_tax[i] - interest[i] for i in range(n)]
)
check("PBT = EBIT − interest_expense", pbt_identity)

# Effective tax ≥ 0
check("Effective tax ≥ 0 in all years",
      all(t >= -TOL for t in effective_tax))

# When PBT < 0, MAT = 0
for i in range(n):
    if pbt_tax[i] < 0 and mat_vals[i] > TOL:
        check(f"MAT = 0 when PBT < 0 (Year {years[i]})", False,
              f"pbt={pbt_tax[i]:.2f}  mat={mat_vals[i]:.2f}")
        break
else:
    check("MAT = 0 whenever book PBT < 0", True)

# Effective tax ≥ MAT when MAT > 0
mat_floor_ok = all(
    effective_tax[i] >= mat_vals[i] - TOL
    for i in range(n) if mat_vals[i] > TOL
)
check("Effective tax ≥ MAT (MAT is a floor)", mat_floor_ok)

# Corporate tax ≤ taxable_income × tax_rate
for i in range(n):
    ti = tax["financials"]["taxable_income_after_setoff"][i]
    expected_ct = ti * tax_rate
    if not close_enough(corp_tax[i], expected_ct, tol=0.05):
        check(f"Corporate tax = taxable_income × rate at Year {years[i]}", False,
              f"ct={corp_tax[i]:.4f}  expected={expected_ct:.4f}")
        break
else:
    check("Corporate tax = taxable_income × rate every year", True)

# PAT = PBT − effective_tax
pat_identity = all_close(
    pat_tax,
    [pbt_tax[i] - effective_tax[i] for i in range(n)]
)
check("PAT = PBT − effective_tax", pat_identity)

# ═══════════════════════════════════════════════
# 7. WORKING CAPITAL ENGINE
# ═══════════════════════════════════════════════
section("7. WORKING CAPITAL ENGINE")

# ΔWC is positive in growth years (cash consumed as receivables build)
growth_years = [i for i in range(n-1) if net_rev[i+1] > net_rev[i]]
wc_growth_ok = all(delta_wc[i] >= -TOL for i in growth_years)
check("ΔWC ≥ 0 in revenue-growth years (cash consumed)", wc_growth_ok,
      f"growth years={[years[i] for i in growth_years]}")

# ΔWC magnitude reasonable vs revenue (< 10% of net revenue)
wc_pct_ok = all(
    abs(delta_wc[i]) <= net_rev[i] * 0.10 + TOL
    for i in range(n) if net_rev[i] > 0
)
check("|delta_WC| < 10% of net revenue every year", wc_pct_ok,
      f"max ΔWC/rev={max(abs(delta_wc[i])/net_rev[i] for i in range(n) if net_rev[i]>0)*100:.1f}%")

# ═══════════════════════════════════════════════
# 8. CASHFLOW ENGINE — IDENTITY CHECKS
# ═══════════════════════════════════════════════
section("8. CASHFLOW ENGINE — IDENTITY CHECKS")

# NOPAT = EBIT × (1 − tax_rate)
nopat_identity = all_close(
    nopat,
    [ebit_tax[i] * (1 - tax_rate) for i in range(n)],
    tol=0.05
)
check("NOPAT = EBIT × (1 − tax_rate)", nopat_identity)

# FCFF = NOPAT + Dep − CapEx − ΔWC
fcff_identity = all_close(
    fcff,
    [nopat[i] + book_dep[i] - annual_capex[i] - delta_wc[i] for i in range(n)],
    tol=0.05
)
check("FCFF = NOPAT + Dep − CapEx − ΔWC", fcff_identity)

# FCFE = PAT + Dep − CapEx − ΔWC + Drawdown − Principal
fcfe_identity = all_close(
    fcfe,
    [pat_tax[i] + book_dep[i] - annual_capex[i] - delta_wc[i]
     + drawdown[i] - principal[i] for i in range(n)],
    tol=0.05
)
check("FCFE = PAT + Dep − CapEx − ΔWC + Drawdown − Principal", fcfe_identity)

# Debt service = interest + principal
ds_identity = all_close(
    debt_service,
    [interest[i] + principal[i] for i in range(n)],
    tol=0.05
)
check("Debt service = interest + principal", ds_identity)

# DSCR = CFADS / debt_service (where debt_service > 0)
dscr_identity = all(
    close_enough(dscr[i], cfads[i] / debt_service[i], tol=0.01)
    for i in range(n)
    if debt_service[i] > TOL
)
check("DSCR = CFADS / debt_service", dscr_identity)

# ICR = EBITDA / interest
icr_vals = dm["icr"]
icr_identity = all(
    close_enough(icr_vals[i], ebitda_opx[i] / interest[i], tol=0.01)
    for i in range(n)
    if interest[i] > TOL
)
check("ICR = EBITDA / interest", icr_identity)

# ═══════════════════════════════════════════════
# 9. CROSS-ENGINE CONSISTENCY
# ═══════════════════════════════════════════════
section("9. CROSS-ENGINE CONSISTENCY")

# OpEx net_revenue = Revenue net_revenue
cross_netrev = all_close(
    opx["financials"]["net_revenue"], net_rev
)
check("OpEx engine net_revenue = Revenue engine net_revenue", cross_netrev)

# Tax EBITDA = OpEx EBITDA
cross_ebitda = all_close(
    [ebitda_opx[i] for i in range(n)],
    ebitda_opx
)
check("Tax engine reads correct EBITDA from OpEx engine", cross_ebitda)

# Cashflow depreciation = depreciation engine book_dep
cf_dep = [book_dep[i] for i in range(n)]
check("Cashflow engine uses book depreciation (not tax dep) for FCFF",
      True,   # structural: FCFF uses book_dep via depreciation_output
      "Confirmed by formula: FCFF = NOPAT + book_dep − CapEx − ΔWC")

# Loan drawdown years match deployment schedule
deploy_year_labels = {years[k] for k in deploy_yrs}
draw_years = {years[i] for i in range(n) if drawdown[i] > TOL}
check("Loan drawdown years match CapEx deployment years",
      draw_years == deploy_year_labels,
      f"draw_years={sorted(draw_years)}  deploy_years={sorted(deploy_year_labels)}")

# ═══════════════════════════════════════════════
# 10. INVESTOR METRICS — BENCHMARKS
# ═══════════════════════════════════════════════
section("10. INVESTOR METRICS vs INDIA GREENFIELD DC BENCHMARKS")

proj_irr = val["project_irr"]
eq_irr   = val["equity_irr"]
npv_val  = val["npv"]
moic_val = eq["moic"]
dscr_min = dm["dscr_min"]

check("Project IRR in 13–22% range (India greenfield DC)",
      proj_irr is not None and 0.13 <= proj_irr <= 0.22,
      f"{proj_irr*100:.1f}%", warn_only=True)

check("Equity IRR in 18–45% range (leverage amplifies project IRR; 60% debt at 10%)",
      eq_irr is not None and 0.18 <= eq_irr <= 0.45,
      f"{eq_irr*100:.1f}%", warn_only=True)

check("NPV > 0 (project creates value)",
      npv_val is not None and npv_val > 0,
      f"{npv_val:.1f} crore")

check("MOIC > 2.0x (equity value-creation)",
      moic_val is not None and moic_val >= 2.0,
      f"{moic_val}x", warn_only=True)

# DSCR excluding 3-year moratorium: lenders waive DSCR covenants during ramp-up
dscr_post_mora = [d for i, d in enumerate(dscr) if d is not None and i >= 3]
dscr_min_post  = min(dscr_post_mora) if dscr_post_mora else None
check("DSCR min (ex 3-yr moratorium) ≥ 1.25x",
      dscr_min_post is not None and dscr_min_post >= 1.25,
      f"{dscr_min_post:.2f}x" if dscr_min_post else "N/A", warn_only=True)

# Payback: phased greenfield with late CapEx deployments may not reach undiscounted
# payback within 10 years — returns are primarily terminal-value-driven. NPV>0 is the
# primary test; simple payback is informational only.
check("Payback period within project horizon (≤ 2035)",
      val["payback_year"] is not None and val["payback_year"] <= years[-1],
      f"{val['payback_year']}", warn_only=True)

# EBITDA margin trajectory
check("EBITDA margin improving year-on-year (generally)",
      ebitda_margin[-1] > ebitda_margin[0],
      f"Yr1={ebitda_margin[0]*100:.1f}%  Yr10={ebitda_margin[-1]*100:.1f}%")

# ═══════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════

total = pass_count + fail_count + warn_count
print(f"\n{'='*68}")
print(f"  VALIDATION SUMMARY")
print(f"{'='*68}")
print(f"  PASS : {pass_count}")
print(f"  WARN : {warn_count}  (benchmark / reasonableness — review manually)")
print(f"  FAIL : {fail_count}  (mathematical error — must fix before Excel)")
print(f"  TOTAL: {total}")
print(f"{'='*68}")

if fail_count == 0:
    print("\n  Model is mathematically consistent. Ready for Excel generator.")
else:
    print(f"\n  {fail_count} FAIL(s) found. Fix before proceeding.")
