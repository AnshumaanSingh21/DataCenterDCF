import pandas as pd


def compute_loan(
    capex_output,
    assumptions
):

    years = len(
        capex_output["metadata"]["years"]
    )

    year_labels = (
        capex_output["metadata"]["years"]
    )

    total_capex = (
        capex_output["financials"]
        ["total_capex"]
    )

    deployment_schedule = (
        capex_output[
            "deployment_schedule"
        ]
    )

    debt_pct = assumptions["debt_pct"]

    equity_pct = 1.0 - debt_pct

    interest_rate = (
        assumptions["interest_rate"]
    )

    tenure = (
        assumptions["loan_tenure_years"]
    )

    moratorium = (
        assumptions["moratorium_years"]
    )

    # ----------------------------------
    # CAPITAL INFUSION
    # ----------------------------------

    debt_funding = [

        x * debt_pct

        for x in total_capex
    ]

    equity_funding = [

        x * equity_pct

        for x in total_capex
    ]

    # ----------------------------------
    # TRANCHE CREATION
    # ----------------------------------

    tranches = []

    for tranche_id, phase in enumerate(
        deployment_schedule,
        start=1
    ):

        draw_year = phase["year"]

        loan_amount = (
            total_capex[draw_year]
            * debt_pct
        )

        opening_balance = [0] * years

        principal_payment = [0] * years

        interest_payment = [0] * years

        closing_balance = [0] * years

        outstanding = loan_amount

        annual_principal = loan_amount / tenure

        repayment_start = draw_year + moratorium + 1

        repayment_end = repayment_start + tenure

        for yr in range(draw_year, years):

            opening_balance[yr] = outstanding

            interest_payment[yr] = outstanding * interest_rate

            if (
                yr >= repayment_start
                and yr < repayment_end
                and outstanding > 0
            ):
                principal_payment[yr] = min(
                    annual_principal,
                    outstanding
                )
                outstanding -= principal_payment[yr]

            closing_balance[yr] = outstanding

        tranches.append({

            "tranche_id":
                tranche_id,

            "draw_year":
                draw_year,

            "loan_amount":
                loan_amount,

            "opening_balance":
                opening_balance,

            "interest_payment":
                interest_payment,

            "principal_payment":
                principal_payment,

            "closing_balance":
                closing_balance
        })

    # ----------------------------------
    # CONSOLIDATED DEBT ACCOUNT
    # ----------------------------------

    opening_balance = [0] * years

    drawdown = [0] * years

    principal_repayment = [0] * years

    interest_expense = [0] * years

    closing_balance = [0] * years

    for year_idx in range(years):

        for tranche in tranches:

            draw_year = (
                tranche["draw_year"]
            )

            if year_idx == draw_year:

                drawdown[year_idx] += (
                    tranche[
                        "loan_amount"
                    ]
                )

            principal_repayment[
                year_idx
            ] += (

                tranche[
                    "principal_payment"
                ][year_idx]
            )

            interest_expense[
                year_idx
            ] += (

                tranche[
                    "interest_payment"
                ][year_idx]
            )

        if year_idx == 0:

            opening_balance[
                year_idx
            ] = 0

        else:

            opening_balance[
                year_idx
            ] = (

                closing_balance[
                    year_idx - 1
                ]
            )

        closing_balance[
            year_idx
        ] = (

            opening_balance[
                year_idx
            ]

            +

            drawdown[
                year_idx
            ]

            -

            principal_repayment[
                year_idx
            ]
        )

    # ----------------------------------
    # DATAFRAME
    # ----------------------------------

    debt_account_df = pd.DataFrame({

        "Year":
            year_labels,

        "Opening Debt":
            opening_balance,

        "Debt Drawdown":
            drawdown,

        "Interest Expense":
            interest_expense,

        "Principal Repaid":
            principal_repayment,

        "Closing Debt":
            closing_balance
    })

    # ----------------------------------
    # OUTPUT
    # ----------------------------------

    return {

        "capital_structure": {

            "debt_funding":
                debt_funding,

            "equity_funding":
                equity_funding
        },

        "long_term_debt_account": {

            "opening_balance":
                opening_balance,

            "drawdown":
                drawdown,

            "principal_repayment":
                principal_repayment,

            "interest_expense":
                interest_expense,

            "closing_balance":
                closing_balance
        },

        "tranches":
            tranches,

        "dataframes": {

            "debt_account_df":
                debt_account_df
        },

        "assumption_register":
            assumptions.copy()
    }