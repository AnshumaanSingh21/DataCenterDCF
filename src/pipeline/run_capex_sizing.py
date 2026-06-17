from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from src.engines.capex_sizing_engine import (
    compute_electrical_sizing
)


capex_assumptions = (
    get_default_capex_assumptions()
)

revenue_assumptions = (
    get_default_revenue_assumptions()
)

total_racks = 1000

kw_per_rack = (
    revenue_assumptions[
        "kw_per_rack"
    ]
)

pue = (
    revenue_assumptions[
        "pue"
    ]
)

results = compute_electrical_sizing(

    total_racks=total_racks,

    kw_per_rack= kw_per_rack,

    pue=pue,

    assumptions=capex_assumptions
)

print("\n==============================")
print("ELECTRICAL SIZING TEST")
print("==============================")

print("\nLOADS")
print(
    results["loads"]
)

print("\nEQUIPMENT COUNTS")
print(
    results["equipment_counts"]
)

print("\nCAPEX BREAKDOWN (Cr)")
print(
    results["capex_breakdown"]
)

print("\nTOTAL ELECTRICAL CAPEX (Cr)")
print(
    results[
        "electrical_capex_total_crore"
    ]
)

print("\nELECTRICAL CAPEX PER RACK (Cr)")
print(
    results[
        "electrical_capex_per_rack_crore"
    ]
)