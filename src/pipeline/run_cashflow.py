import pandas as pd

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

pd.set_option("display.width", 220)
pd.set_option("display.float_format", "{:.2f}".format)

user_inputs = {
    "location":            "Mumbai",
    "total_racks":         1000,
    "facility_type":       "retail_colo",
    "projection_years":    10,
    "start_year":          2026,
    "deployment_schedule": {0: 300, 3: 300, 6: 400},
}

# ----------------------------------
# RUN ALL ENGINES
# ----------------------------------

revenue_output = compute_revenue(
    user_inputs, get_default_revenue_assumptions()
)

capex_output = compute_capex(
    user_inputs, get_default_capex_assumptions()
)

opex_output = compute_opex(
    revenue_output, capex_output, get_default_opex_assumptions()
)

depreciation_output = compute_depreciation(
    capex_output, get_default_depreciation_assumptions()
)

loan_output = compute_loan(
    capex_output, get_default_loan_assumptions()
)

tax_output = compute_tax(
    opex_output, depreciation_output, loan_output,
    get_default_tax_assumptions()
)

working_capital_output = compute_working_capital(
    revenue_output, get_default_working_capital_assumptions()
)

cashflow_output = compute_cashflow(
    opex_output,
    capex_output,
    depreciation_output,
    loan_output,
    tax_output,
    working_capital_output,
    valuation_assumptions=get_default_valuation_assumptions(),
)

# ----------------------------------
# DISPLAY
# ----------------------------------

sep = lambda t: print(f"\n{'='*70}\n  {t}\n{'='*70}")

sep("P&L STATEMENT (crore)")
print(cashflow_output["dataframes"]["pnl_df"].to_string(index=False))

sep("CASHFLOW STATEMENT (crore)")
print(cashflow_output["dataframes"]["cashflow_df"].to_string(index=False))

sep("DEBT & COVERAGE METRICS")
print(cashflow_output["dataframes"]["debt_df"].to_string(index=False))

sep("SOURCES & USES (crore)")
print(cashflow_output["dataframes"]["su_df"].to_string(index=False))

sep("EQUITY SCHEDULE (crore)")
print(cashflow_output["dataframes"]["equity_df"].to_string(index=False))

sep("INVESTOR SUMMARY")
val = cashflow_output["valuation"]
eq  = cashflow_output["equity"]
dm  = cashflow_output["debt_metrics"]

print(f"  WACC                    : {val['wacc']*100:.1f}%")
print(f"    Cost of Equity        : {val['cost_of_equity']*100:.1f}%")
print(f"    Cost of Debt (post-tx): {val['cost_of_debt_post_tax']*100:.1f}%")
print(f"  Terminal Value          : {val['terminal_value']:.1f} crore  ({val['terminal_method']})")
print(f"  NPV                     : {val['npv']:.1f} crore")
print()
print(f"  Project IRR             : {val['project_irr']*100:.1f}%")
print(f"  Equity IRR              : {val['equity_irr']*100:.1f}%")
print(f"  Payback Period          : {val['payback_year']}")
print(f"  Discounted Payback      : {val['discounted_payback_year']}")
print()
print(f"  Total Equity Invested   : {eq['total_equity_invested']:.1f} crore")
print(f"  Total Equity Returned   : {eq['total_equity_returned']:.1f} crore")
print(f"  MOIC                    : {eq['moic']}x")
print()
print(f"  DSCR Min                : {dm['dscr_min']}x")
print(f"  DSCR Covenant (>{dm['dscr_covenant']}x)")
print(f"  DSCR Breaches           : {dm['dscr_breaches'] or 'None'}")
