from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from assumptions.opex_defaults import (
    get_default_opex_assumptions
)

from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

from assumptions.depreciation_defaults import (
    get_default_depreciation_assumptions
)

from assumptions.loan_defaults import (
    get_default_loan_assumptions
)

from assumptions.tax_defaults import (
    get_default_tax_assumptions
)

from assumptions.working_capital_defaults import (
    get_default_working_capital_assumptions
)

from src.engines.revenue_engine import (
    compute_revenue
)

from src.engines.opex_engine import (
    compute_opex
)

from src.engines.capex_engine import (
    compute_capex
)

from src.engines.depreciation_engine import (
    compute_depreciation
)

from src.engines.loan_engine import (
    compute_loan
)

from src.engines.tax_engine import (
    compute_tax
)

from src.engines.working_capital_engine import (
    compute_working_capital
)

from src.engines.cashflow_engine import (
    compute_cashflow
)


user_inputs = {

    "location": "Mumbai",

    "total_racks": 1000,

    "facility_type": "wholesale",

    "projection_years": 10
}

# ----------------------------------
# REVENUE
# ----------------------------------

revenue_output = compute_revenue(

    user_inputs,

    get_default_revenue_assumptions()
)

# ----------------------------------
# CAPEX
# ----------------------------------

capex_output = compute_capex(

    user_inputs,

    get_default_capex_assumptions()
)

# ----------------------------------
# OPEX
# ----------------------------------

opex_output = compute_opex(

    revenue_output,

    capex_output,

    get_default_opex_assumptions()
)

# ----------------------------------
# DEPRECIATION
# ----------------------------------

depreciation_output = compute_depreciation(

    capex_output,

    get_default_depreciation_assumptions()
)

# ----------------------------------
# LOAN
# ----------------------------------

loan_output = compute_loan(

    capex_output,

    get_default_loan_assumptions()
)

# ----------------------------------
# TAX
# ----------------------------------

tax_output = compute_tax(

    opex_output,

    depreciation_output,

    loan_output,

    get_default_tax_assumptions()
)

# ----------------------------------
# WORKING CAPITAL
# ----------------------------------

working_capital_output = compute_working_capital(

    revenue_output,

    get_default_working_capital_assumptions()
)

# ----------------------------------
# CASH FLOW
# ----------------------------------

cashflow_output = compute_cashflow(

    opex_output,

    capex_output,

    depreciation_output,

    loan_output,

    tax_output,

    working_capital_output

)

print("\n==============================")
print("CASH FLOW MODEL TEST")
print("==============================")

print("\nFCFF")
print(
    cashflow_output["financials"]
    ["fcff"]
)

print("\nFCFE")
print(
    cashflow_output["financials"]
    ["fcfe"]
)

print("\nDSCR")
print(
    cashflow_output["financials"]
    ["dscr"]
)

print("\nPROJECT IRR")
print(
    cashflow_output["financials"]
    ["project_irr"]
)

print("\nEQUITY IRR")
print(
    cashflow_output["financials"]
    ["equity_irr"]
)

print("\nCASHFLOW TABLE")
print(
    cashflow_output["dataframes"]
    ["cashflow_df"]
)