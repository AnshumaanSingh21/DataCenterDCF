from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from src.engines.revenue_engine import (
    compute_revenue
)

from src.reporting.revenue_report import (
    export_revenue_report
)


user_inputs = {

    "location": "Mumbai",

    "total_racks": 1000,

    "facility_type": "wholesale",

    "projection_years": 10
}

assumptions = (
    get_default_revenue_assumptions()
)

revenue_output = compute_revenue(
    user_inputs,
    assumptions
)

export_revenue_report(
    revenue_output,
    "outputs/revenue/revenue_projection.xlsx"
)