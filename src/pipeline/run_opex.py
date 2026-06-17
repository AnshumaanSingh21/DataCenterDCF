from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

from src.engines.capex_engine import (
    compute_capex
)

from assumptions.opex_defaults import (
    get_default_opex_assumptions
)

from src.engines.revenue_engine import (
    compute_revenue
)

from src.engines.opex_engine import (
    compute_opex
)

from src.reporting.opex_report import (
    export_opex_report
)


user_inputs = {

    "location": "Mumbai",

    "total_racks": 1000,

    "facility_type": "wholesale",

    "projection_years": 10,
}

# -----------------------------
# REVENUE
# -----------------------------

revenue_output = compute_revenue(

    user_inputs,

    get_default_revenue_assumptions()
)

# -----------------------------
# CAPEX
# -----------------------------

capex_output = compute_capex(

    user_inputs,

    get_default_capex_assumptions()
)

import inspect

print("\n===== DEBUG =====")
print(inspect.signature(compute_opex))

# -----------------------------
# OPEX
# -----------------------------

opex_output = compute_opex(

    revenue_output,

    capex_output,

    get_default_opex_assumptions()
)

# -----------------------------
# CONSOLE OUTPUT
# -----------------------------

print("\n==============================")
print("OPEX MODEL TEST")
print("==============================")

print("\nFTE COUNT")
print(
    opex_output["drivers"]
    ["fte_count"]
)

print("\nTOTAL OPEX")
print(
    opex_output["financials"]
    ["total_opex"]
)

print("\nEBITDA")
print(
    opex_output["financials"]
    ["ebitda"]
)

print("\nEBITDA MARGIN")
print(
    opex_output["financials"]
    ["ebitda_margin"]
)
print("\nFACILITY SQFT")
print(
    opex_output["drivers"]
    ["facility_sqft"]
)

print("\nHOUSEKEEPING COST")
print(
    opex_output["cost_lines"]
    ["housekeeping_cost"]
)

print("\nINSURANCE COST")
print(
    opex_output["cost_lines"]
    ["insurance_cost"]
)

print("\nPROPERTY TAX")
print(
    opex_output["cost_lines"]
    ["property_tax"]
)

print("\nMAINTENANCE COST")
print(
    opex_output["cost_lines"]
    ["maintenance_cost"]
)

# -----------------------------
# EXCEL EXPORT
# -----------------------------

export_opex_report(

    opex_output,

    "outputs/opex/opex_projection.xlsx"
)