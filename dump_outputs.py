import sys
sys.path.insert(0, ".")

from assumptions.revenue_defaults import get_default_revenue_assumptions, FACILITY_TYPE_OVERRIDES
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

user_inputs = {
    "total_racks": 1000,
    "location": "Mumbai",
    "facility_type": "retail_colo",
    "start_year": 2026,
    "projection_years": 10,
    "deployment_schedule": {0: 300, 3: 300, 6: 400},
}

rev  = compute_revenue(user_inputs, get_default_revenue_assumptions())
cap  = compute_capex(user_inputs, get_default_capex_assumptions())
opx  = compute_opex(rev, cap, get_default_opex_assumptions())
dep  = compute_depreciation(cap, get_default_depreciation_assumptions())
loan = compute_loan(cap, get_default_loan_assumptions())
tax  = compute_tax(opx, dep, loan, get_default_tax_assumptions())
wc   = compute_working_capital(rev, get_default_working_capital_assumptions())
cf   = compute_cashflow(opx, cap, dep, loan, tax, wc, get_default_valuation_assumptions())

years = rev["metadata"]["years"]
n = len(years)

def hdr(title):
    print()
    print("=" * 90)
    print(f"  {title}")
    print("=" * 90)

# ------------------------------------------------------------------
# REVENUE
# ------------------------------------------------------------------
hdr("REVENUE (crore)")
occ      = rev["drivers"]["occupied_racks"]
deployed = [sum(user_inputs["deployment_schedule"].get(j, 0) for j in range(i+1)) for i in range(n)]
colo_rev = rev["revenue_streams"]["recurring_colo_revenue"]
pwr_rev  = rev["revenue_streams"]["power_revenue"]
otc_rev  = rev["revenue_streams"]["otc_setup_revenue"]
gross    = rev["revenue_streams"]["gross_revenue"]
net_rev  = rev["revenue_streams"]["net_revenue"]
rack_mrc = rev["drivers"]["rack_mrc"]
new_racks = rev["drivers"]["new_racks"]

print(f"{'Year':<6} {'Deploy':>7} {'Occupy':>7} {'NewRks':>7} {'MRC/rack':>10} {'ColoRev':>9} {'PowerRev':>9} {'OTC':>7} {'Gross':>9} {'Net':>9}")
for i, y in enumerate(years):
    mrc_k = rack_mrc[i] * 1e7 / 1000   # crore -> Rs thousands
    print(f"{y:<6} {deployed[i]:>7.0f} {occ[i]:>7.0f} {new_racks[i]:>7.0f} {mrc_k:>9.1f}K {colo_rev[i]:>9.2f} {pwr_rev[i]:>9.2f} {otc_rev[i]:>7.3f} {gross[i]:>9.2f} {net_rev[i]:>9.2f}")

# ------------------------------------------------------------------
# CAPEX
# ------------------------------------------------------------------
hdr("CAPEX (crore)")
capex_v    = cap["financials"]["total_capex"]
cumcap     = cap["financials"]["cumulative_capex"]
cap_comps  = cap["capex_components"]

comp_names = list(cap_comps.keys())
header = f"{'Year':<6} {'CapEx':>8} {'CumCapEx':>10}  " + "  ".join(f"{k[:9]:>9}" for k in comp_names)
print(header)
for i, y in enumerate(years):
    row = f"{y:<6} {capex_v[i]:>8.2f} {cumcap[i]:>10.2f}  "
    row += "  ".join(f"{cap_comps[k][i]:>9.2f}" for k in comp_names)
    print(row)

land = cap["site_sizing"]["land_cost_crore"]
print(f"\n  Land cost (included in civil): Rs {land:.2f} crore")
print(f"  Total project CapEx:           Rs {sum(capex_v):.2f} crore")
print(f"  CapEx per rack:                Rs {sum(capex_v)/1000*100:.1f} lakh/rack")

# ------------------------------------------------------------------
# OPEX
# ------------------------------------------------------------------
hdr("OPEX & EBITDA (crore)")
cl         = opx["cost_lines"]
cost_names = list(cl.keys())
totopx     = opx["financials"]["total_opex"]
ebitda     = opx["financials"]["ebitda"]
ebitdam    = opx["financials"]["ebitda_margin"]

header = f"{'Year':<6} " + " ".join(f"{k[:9]:>9}" for k in cost_names) + f" {'Total':>8} {'EBITDA':>8} {'Marg%':>6}"
print(header)
for i, y in enumerate(years):
    row = f"{y:<6} " + " ".join(f"{cl[k][i]:>9.2f}" for k in cost_names)
    row += f" {totopx[i]:>8.2f} {ebitda[i]:>8.2f} {ebitdam[i]*100:>5.1f}%"
    print(row)

# ------------------------------------------------------------------
# DEPRECIATION
# ------------------------------------------------------------------
hdr("DEPRECIATION (crore)")
book_dep  = dep["financials"]["total_depreciation"]
tax_dep   = dep["financials"]["tax_depreciation"]
accum_dep = dep["financials"]["accumulated_depreciation"]
nbv       = dep["financials"]["net_book_value"]

print(f"{'Year':<6} {'BookDep(SLM)':>13} {'TaxDep(WDV)':>13} {'AccumDep':>10} {'NBV':>10} {'AccumDep/CumCapEx':>18}")
for i, y in enumerate(years):
    ratio = accum_dep[i] / cumcap[i] * 100 if cumcap[i] > 0 else 0
    print(f"{y:<6} {book_dep[i]:>13.2f} {tax_dep[i]:>13.2f} {accum_dep[i]:>10.2f} {nbv[i]:>10.2f} {ratio:>17.1f}%")

# ------------------------------------------------------------------
# LOAN
# ------------------------------------------------------------------
hdr("LOAN SCHEDULE (crore)")
ld         = loan["long_term_debt_account"]
drawdown   = ld["drawdown"]
interest   = ld["interest_expense"]
principal  = ld["principal_repayment"]
closing    = ld["closing_balance"]
opening    = ld["opening_balance"]
eq_funding = loan["capital_structure"]["equity_funding"]

print(f"{'Year':<6} {'Opening':>9} {'Drawdown':>9} {'Equity':>8} {'Interest':>9} {'Principal':>10} {'Closing':>9} {'IntRate%':>9}")
for i, y in enumerate(years):
    int_rate = interest[i] / opening[i] * 100 if opening[i] > 0 else 0
    print(f"{y:<6} {opening[i]:>9.2f} {drawdown[i]:>9.2f} {eq_funding[i]:>8.2f} {interest[i]:>9.2f} {principal[i]:>10.2f} {closing[i]:>9.2f} {int_rate:>8.1f}%")

print(f"\n  Total debt drawn:    Rs {sum(drawdown):.2f} crore")
print(f"  Total equity:        Rs {sum(eq_funding):.2f} crore")
print(f"  Total interest paid: Rs {sum(interest):.2f} crore")
print(f"  Total principal pd:  Rs {sum(principal):.2f} crore")
print(f"  Residual closing:    Rs {closing[-1]:.2f} crore")

# ------------------------------------------------------------------
# P&L
# ------------------------------------------------------------------
hdr("P&L (crore)")
ebit_v  = tax["financials"]["ebit"]
pbt_v   = tax["financials"]["pbt"]
tax_v   = tax["financials"]["tax"]
pat_v   = tax["financials"]["pat"]

print(f"{'Year':<6} {'NetRev':>8} {'OpEx':>8} {'EBITDA':>8} {'BookDep':>8} {'EBIT':>8} {'Interest':>9} {'PBT':>8} {'Tax':>8} {'PAT':>8}")
for i, y in enumerate(years):
    print(f"{y:<6} {net_rev[i]:>8.2f} {totopx[i]:>8.2f} {ebitda[i]:>8.2f} {book_dep[i]:>8.2f} {ebit_v[i]:>8.2f} {interest[i]:>9.2f} {pbt_v[i]:>8.2f} {tax_v[i]:>8.2f} {pat_v[i]:>8.2f}")

# ------------------------------------------------------------------
# WORKING CAPITAL
# ------------------------------------------------------------------
hdr("WORKING CAPITAL (crore)")
delta_wc = wc["financials"]["change_in_working_capital"]
wc_keys  = [k for k in wc["financials"].keys() if k != "change_in_working_capital"]

print(f"{'Year':<6} {'DeltaWC':>9} {'% of Rev':>9}")
for i, y in enumerate(years):
    pct = delta_wc[i] / net_rev[i] * 100 if net_rev[i] != 0 else 0
    print(f"{y:<6} {delta_wc[i]:>9.2f} {pct:>8.1f}%")

# ------------------------------------------------------------------
# CASHFLOW
# ------------------------------------------------------------------
hdr("CASHFLOW (crore)")
cflows    = cf["cashflows"]
fcff_v    = cflows["fcff"]
cumfcff   = cflows["cumulative_fcff"]
fcfe_v    = cflows["fcfe"]
cfads_v   = cflows["cfads"]
ds_v      = cflows["debt_service"]
dscr_v    = cflows["dscr"]
maint_cx  = cflows["maintenance_capex"]
nopat_v   = [ebit_v[i] * (1 - 0.25) for i in range(n)]

print(f"{'Year':<6} {'NOPAT':>8} {'CapEx':>8} {'MaintCx':>8} {'BookDep':>8} {'DeltaWC':>8} {'FCFF':>8} {'CumFCFF':>9} {'FCFE':>8} {'CFADS':>8} {'DS':>8} {'DSCR':>7}")
for i, y in enumerate(years):
    dscr_s = f"{dscr_v[i]:.2f}" if dscr_v[i] is not None else "  N/A"
    print(f"{y:<6} {nopat_v[i]:>8.2f} {capex_v[i]:>8.2f} {maint_cx[i]:>8.2f} {book_dep[i]:>8.2f} {delta_wc[i]:>8.2f} {fcff_v[i]:>8.2f} {cumfcff[i]:>9.2f} {fcfe_v[i]:>8.2f} {cfads_v[i]:>8.2f} {ds_v[i]:>8.2f} {dscr_s:>7}")

# ------------------------------------------------------------------
# INVESTOR METRICS
# ------------------------------------------------------------------
hdr("INVESTOR METRICS")
iv = cf["valuation"]
eq = cf["equity"]
print(f"  WACC:                    {iv['wacc']*100:.2f}%")
print(f"  Cost of equity:          {iv['cost_of_equity']*100:.1f}%")
print(f"  Cost of debt (post-tax): {iv['cost_of_debt_post_tax']*100:.2f}%")
print()
print(f"  Project IRR:             {iv['project_irr']*100:.1f}%")
print(f"  Equity IRR:              {iv['equity_irr']*100:.1f}%")
print(f"  NPV (at WACC):           Rs {iv['npv']:.2f} crore")
print(f"  Terminal Value:          Rs {iv['terminal_value']:.2f} crore  [{iv['terminal_method']}]")
print(f"  MOIC:                    {iv['moic']:.2f}x")
print(f"  Payback Year:            {iv['payback_year']}")
print(f"  Disc Payback Year:       {iv['discounted_payback_year']}")
print()
print(f"  Total equity invested:   Rs {eq['total_equity_invested']:.2f} crore")
print(f"  Total equity returned:   Rs {eq['total_equity_returned']:.2f} crore")

# ------------------------------------------------------------------
# SOURCES & USES
# ------------------------------------------------------------------
hdr("SOURCES & USES BY PHASE")
for row in cf["sources_and_uses"]:
    y = row["year"]
    debt_pct = row["debt"] / row["total_capex"] * 100 if row["total_capex"] else 0
    eq_pct   = row["equity"] / row["total_capex"] * 100 if row["total_capex"] else 0
    print(f"  {str(y):<6}  CapEx={row['total_capex']:>7.2f}  Debt={row['debt']:>7.2f} ({debt_pct:.0f}%)  Equity={row['equity']:>7.2f} ({eq_pct:.0f}%)")
