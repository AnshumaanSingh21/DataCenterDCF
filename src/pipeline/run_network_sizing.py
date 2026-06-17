from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

from src.engines.network_sizing_engine import (
    compute_network_sizing
)

assumptions = (
    get_default_capex_assumptions()
)

output = compute_network_sizing(

    total_racks=1000,

    assumptions=assumptions
)

print("\n==============================")
print("NETWORK SIZING TEST")
print("==============================")

print("\nTOTAL NETWORK CAPEX (Cr)")
print(
    output[
        "total_network_capex_crore"
    ]
)

print("\nNETWORK CAPEX PER RACK (Cr)")
print(
    output[
        "network_cost_per_rack_crore"
    ]
)

print("\nQUANTITIES")
print(
    output[
        "quantities"
    ]
)

print("\nCOST BREAKDOWN")
print(
    output[
        "cost_breakdown"
    ]
)