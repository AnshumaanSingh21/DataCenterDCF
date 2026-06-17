from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from assumptions.working_capital_defaults import (
    get_default_working_capital_assumptions
)

from src.engines.revenue_engine import (
    compute_revenue
)

user_inputs = {

    "location": "Mumbai",

    "total_racks": 1000,

    "facility_type": "wholesale",

    "projection_years": 10
}

revenue_output = compute_revenue(

    user_inputs,

    get_default_revenue_assumptions()
)

from src.engines.working_capital_engine import (
    compute_working_capital
)

wc_output = compute_working_capital(

    revenue_output,

    get_default_working_capital_assumptions()
)

print(
    wc_output["dataframes"]
    ["working_capital_df"]
)