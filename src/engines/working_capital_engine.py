import pandas as pd


def compute_working_capital(
    revenue_output,
    assumptions,
    opex_output=None
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

    # ----------------------------------
    # WORKING CAPITAL
    # Preferred: DSO/DPO method —
    #   Receivables = net revenue   × DSO / 365
    #   Payables    = CASH opex     × DPO / 365   (depreciation/amortization
    #                 are not in total_opex, so this is already cash-only)
    #   Net WC      = Receivables + Inventory − Payables
    # Falls back to the legacy %-of-revenue method when opex isn't supplied
    # or the day assumptions are missing.
    # ----------------------------------

    receivable_days = assumptions.get("receivable_days")
    payable_days    = assumptions.get("payable_days")
    inventory_days  = assumptions.get("inventory_days", 0)

    use_days = (
        opex_output is not None
        and receivable_days is not None
        and payable_days is not None
    )

    if use_days:
        cash_opex = opex_output["financials"]["total_opex"]
        receivables = [revenue[i]   * receivable_days / 365.0 for i in range(years)]
        payables    = [cash_opex[i] * payable_days    / 365.0 for i in range(years)]
        inventory   = [cash_opex[i] * inventory_days  / 365.0 for i in range(years)]
        working_capital = [
            receivables[i] + inventory[i] - payables[i]
            for i in range(years)
        ]
        method = "dso_dpo"
    else:
        wc_pct = assumptions["working_capital_pct_revenue"]
        receivables = [None] * years
        payables    = [None] * years
        inventory   = [None] * years
        working_capital = [rev * wc_pct for rev in revenue]
        method = "pct_revenue"

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

        "Receivables":
            receivables,

        "Payables":
            payables,

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
                change_in_wc,

            "receivables":
                receivables,

            "payables":
                payables,

            "method":
                method
        },

        "dataframes": {

            "working_capital_df":
                working_capital_df
        },

        "assumption_register":
            assumptions.copy()
    }