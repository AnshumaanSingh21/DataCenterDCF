# NOTE: not part of the live application. A standalone manual runner, not
# imported by src/api/main.py. The live pipeline is wired directly in main.py
# and mirrored in test_model_integrity.py::run_model().

from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

from src.engines.capex_engine import (
    compute_capex
)

from src.reporting.capex_report import (
    export_capex_report
)


user_inputs = {

    "location": "Mumbai",

    "total_racks": 1000,

    "facility_type": "wholesale",

    "projection_years": 10
}

capex_output = compute_capex(

    user_inputs,

    get_default_capex_assumptions()
)

print("\n==============================")
print("CAPEX MODEL TEST")
print("==============================")

print("\nRACKS DEPLOYED")
print(
    capex_output["drivers"]
    ["racks_deployed"]
)

print("\nTOTAL CAPEX")
print(
    capex_output["financials"]
    ["total_capex"]
)

print("\nCUMULATIVE CAPEX")
print(
    capex_output["financials"]
    ["cumulative_capex"]
)


export_capex_report(

    capex_output,

    "outputs/capex/capex_projection.xlsx"
)