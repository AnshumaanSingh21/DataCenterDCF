# NOTE: not part of the live application. A standalone manual runner, not
# imported by src/api/main.py. The live pipeline is wired directly in main.py
# and mirrored in test_model_integrity.py::run_model().

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

    "facility_type": "retail_colo",

    "projection_years": 10,

    "start_year": 2026,

    "deployment_schedule": {
        0: 300,
        3: 300,
        6: 400
    }
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