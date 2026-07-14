# NOTE: not part of the live application. A standalone manual runner, not
# imported by src/api/main.py. The live pipeline is wired directly in main.py
# and mirrored in test_model_integrity.py::run_model().

from src.engines.it_sizing_engine import (
    compute_it_sizing
)

from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

# ----------------------------------
# ASSUMPTIONS
# ----------------------------------

revenue_assumptions = (
    get_default_revenue_assumptions()
)

capex_assumptions = (
    get_default_capex_assumptions()
)

# ----------------------------------
# RUN ENGINE
# ----------------------------------

output = compute_it_sizing(

    total_racks=1000,

    managed_services_penetration=
        revenue_assumptions[
            "managed_services_penetration"
        ],

    assumptions=
        capex_assumptions
)

# ----------------------------------
# RESULTS
# ----------------------------------

print("\n==============================")
print("IT SIZING MODEL TEST")
print("==============================")

print("\nMANAGED RACKS")

print(
    output[
        "managed_racks"
    ]
)

print("\nMANAGED CAPEX PER RACK (Cr)")

print(
    output[
        "managed_capex_per_rack_crore"
    ]
)

print("\nTOTAL MANAGED IT CAPEX (Cr)")

print(
    output[
        "total_managed_it_capex_crore"
    ]
)

print("\nCOST BREAKDOWN")

print(
    output[
        "cost_breakdown"
    ]
)

print("\nSUMMARY TABLE")

print(
    output[
        "dataframes"
    ]["summary_df"]
)