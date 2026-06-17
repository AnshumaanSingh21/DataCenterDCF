from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from src.engines.site_sizing_engine import (
    compute_site_sizing
)

# ----------------------------------
# ASSUMPTIONS
# ----------------------------------

capex_assumptions = (
    get_default_capex_assumptions()
)

revenue_assumptions = (
    get_default_revenue_assumptions()
)

# ----------------------------------
# RUN ENGINE
# ----------------------------------

output = compute_site_sizing(

    total_racks=1000,

    kw_per_rack=
        revenue_assumptions[
            "kw_per_rack"
        ],

    assumptions=
        capex_assumptions
)

# ----------------------------------
# RESULTS
# ----------------------------------

print("\n==============================")
print("SITE SIZING MODEL TEST")
print("==============================")

print("\nLAND AREA (ACRES)")

print(
    output[
        "land_area_acres"
    ]
)

print("\nFACILITY AREA (SQFT)")

print(
    output[
        "facility_sqft"
    ]
)

print("\nIT POWER (MW)")

print(
    output[
        "total_it_power_mw"
    ]
)

print("\nLAND COST (Cr)")

print(
    output[
        "land_cost_crore"
    ]
)

print("\nSUMMARY TABLE")

print(
    output[
        "dataframes"
    ]["summary_df"]
)