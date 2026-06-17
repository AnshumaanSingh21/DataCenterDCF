from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

from assumptions.depreciation_defaults import (
    get_default_depreciation_assumptions
)

from src.engines.capex_engine import (
    compute_capex
)

from src.engines.depreciation_engine import (
    compute_depreciation
)


user_inputs = {

    "location": "Mumbai",

    "total_racks": 1000,

    "facility_type": "wholesale",

    "projection_years": 10
}


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

print("\n==============================")
print("DEPRECIATION MODEL TEST")
print("==============================")

print("\nTOTAL DEPRECIATION")

print(
    depreciation_output["financials"]
    ["total_depreciation"]
)

print("\nACCUMULATED DEPRECIATION")

print(
    depreciation_output["financials"]
    ["accumulated_depreciation"]
)

print("\nNET BOOK VALUE")

print(
    depreciation_output["financials"]
    ["net_book_value"]
)

print("\nDEPRECIATION TABLE")

print(
    depreciation_output["dataframes"]
    ["depreciation_df"]
)