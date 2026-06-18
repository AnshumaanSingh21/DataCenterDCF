import pandas as pd


def compute_working_capital(
    revenue_output,
    assumptions
):

    years = len(
        revenue_output["metadata"]["years"]
    )

    year_labels = (
        revenue_output["metadata"]["years"]
    )

    revenue = (
        revenue_output["revenue_streams"]
        ["net_revenue"]
    )

    wc_pct = (
        assumptions[
            "working_capital_pct_revenue"
        ]
    )

    # ----------------------------------
    # WORKING CAPITAL
    # ----------------------------------

    working_capital = [

        rev * wc_pct

        for rev in revenue
    ]

    # ----------------------------------
    # CHANGE IN WORKING CAPITAL
    # ----------------------------------

    change_in_wc = []

    for i in range(years):

        if i == 0:

            change_in_wc.append(
                working_capital[i]
            )

        else:

            change_in_wc.append(

                working_capital[i]

                -

                working_capital[i - 1]
            )

    # ----------------------------------
    # DATAFRAME
    # ----------------------------------

    working_capital_df = pd.DataFrame({

        "Year":
            year_labels,

        "Revenue":
            revenue,

        "Working Capital":
            working_capital,

        "Change in Working Capital":
            change_in_wc
    })

    # ----------------------------------
    # OUTPUT
    # ----------------------------------

    return {

        "financials": {

            "working_capital":
                working_capital,

            "change_in_working_capital":
                change_in_wc
        },

        "dataframes": {

            "working_capital_df":
                working_capital_df
        },

        "assumption_register":
            assumptions.copy()
    }