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
# OPEX
# ----------------------------------

opex_output = compute_opex(

    revenue_output,

    get_default_opex_assumptions()
)

# ----------------------------------
# CAPEX
# ----------------------------------

capex_output = compute_capex(

    user_inputs,

    get_default_capex_assumptions()
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

print("\n==============================")
print("TAX MODEL TEST")
print("==============================")

print("\nEBIT")

print(
    tax_output["financials"]
    ["ebit"]
)

print("\nPBT")

print(
    tax_output["financials"]
    ["pbt"]
)

print("\nTAX")

print(
    tax_output["financials"]
    ["tax"]
)

print("\nPAT")

print(
    tax_output["financials"]
    ["pat"]
)

print("\nTAX TABLE")

print(
    tax_output["dataframes"]
    ["tax_df"]
)