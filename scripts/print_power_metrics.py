import os
os.environ['PYTHONPATH'] = '.'

from assumptions.revenue_defaults import get_default_revenue_assumptions
from assumptions.capex_defaults import get_default_capex_assumptions
from assumptions.opex_defaults import get_default_opex_assumptions
from assumptions.depreciation_defaults import get_default_depreciation_assumptions
from assumptions.loan_defaults import get_default_loan_assumptions
from assumptions.tax_defaults import get_default_tax_assumptions
from assumptions.working_capital_defaults import get_default_working_capital_assumptions

from src.engines.revenue_engine import compute_revenue
from src.engines.capex_engine import compute_capex
from src.engines.opex_engine import compute_opex
from src.engines.depreciation_engine import compute_depreciation
from src.engines.loan_engine import compute_loan
from src.engines.tax_engine import compute_tax
from src.engines.working_capital_engine import compute_working_capital
from src.engines.cashflow_engine import compute_cashflow

user_inputs = {
    "location": "Mumbai",
    "total_racks": 1000,
    "facility_type": "wholesale",
    "projection_years": 10
}

revenue_output = compute_revenue(user_inputs, get_default_revenue_assumptions())
capex_output = compute_capex(user_inputs, get_default_capex_assumptions())
opex_output = compute_opex(revenue_output, capex_output, get_default_opex_assumptions())
depreciation_output = compute_depreciation(capex_output, get_default_depreciation_assumptions())
loan_output = compute_loan(capex_output, get_default_loan_assumptions())
tax_output = compute_tax(opex_output, depreciation_output, loan_output, get_default_tax_assumptions())
working_capital_output = compute_working_capital(revenue_output, get_default_working_capital_assumptions())
cashflow_output = compute_cashflow(opex_output, capex_output, depreciation_output, loan_output, tax_output, working_capital_output)

power_revenue = revenue_output["revenue_streams"]["power_revenue"]
power_cost = revenue_output["financials"]["power_cost"]
power_margin = revenue_output["financials"]["power_margin"]

dscr = cashflow_output["financials"]["dscr"]

print("Power Revenue (Cr):")
print([round(x,6) for x in power_revenue])
print("Power Cost (Cr):")
print([round(x,6) for x in power_cost])
print("Power Margin (Cr):")
print([round(x,6) for x in power_margin])
print("\nYear 1 DSCR:", round(dscr[0],6))

# Also output full IRRs for later comparison
project_irr = cashflow_output['financials']['project_irr']
equity_irr = cashflow_output['financials']['equity_irr']
print("\nProject IRR:", round(project_irr*100,6))
print("Equity IRR:", round(equity_irr*100,6))

# DSCR minima
_dscr = cashflow_output['financials']['dscr']
min_dscr = min([x for x in _dscr if x is not None])
min_dscr_yr = cashflow_output['dataframes']['cashflow_df']['Year'][_dscr.index(min_dscr)]
print("Min DSCR:", round(min_dscr,6))
print("Min DSCR Year:", min_dscr_yr)
