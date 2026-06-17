import pandas as pd


def compute_tax(
    opex_output,
    depreciation_output,
    loan_output,
    assumptions
):

    years = len(
        opex_output["metadata"]["years"]
    )

    year_labels = (
        opex_output["metadata"]["years"]
    )

    ebitda = (
        opex_output["financials"]
        ["ebitda"]
    )

    depreciation = (
        depreciation_output["financials"]
        ["total_depreciation"]
    )

    interest_expense = (
        loan_output[
            "long_term_debt_account"
        ]["interest_expense"]
    )

    tax_rate = (
        assumptions[
            "corporate_tax_rate"
        ]
    )

    # ----------------------------------
    # EBIT
    # ----------------------------------

    ebit = [

        ebitda[i]

        -

        depreciation[i]

        for i in range(years)
    ]

    # ----------------------------------
    # PBT
    # ----------------------------------

    pbt = [

        ebit[i]

        -

        interest_expense[i]

        for i in range(years)
    ]

    # ----------------------------------
    # TAX LOSS CARRY FORWARD
    # ----------------------------------

    tax = []

    tax_losses_brought_forward = []

    taxable_income_after_setoff = []

    closing_tax_losses = []

    loss_pool = 0

    for i in range(years):

        opening_loss_pool = loss_pool

        current_pbt = pbt[i]

        if current_pbt < 0:

            taxable_income = 0

            loss_pool += abs(
                current_pbt
            )

            current_tax = 0

        else:

            taxable_income = max(

                current_pbt

                - loss_pool,

                0
            )

            loss_utilized = min(

                loss_pool,

                current_pbt
            )

            loss_pool -= loss_utilized

            current_tax = (

                taxable_income

                * tax_rate
            )

        tax.append(
            current_tax
        )

        tax_losses_brought_forward.append(
            opening_loss_pool
        )

        taxable_income_after_setoff.append(
            taxable_income
        )

        closing_tax_losses.append(
            loss_pool
        )

   
    # ----------------------------------
    # PAT
    # ----------------------------------

    pat = [

        pbt[i]

        -

        tax[i]

        for i in range(years)
    ]

    # ----------------------------------
    # TAX DATAFRAME
    # ----------------------------------

    tax_df = pd.DataFrame({

        "Year":
            year_labels,

        "EBITDA":
            ebitda,

        "Depreciation":
            depreciation,

        "EBIT":
            ebit,

        "Interest Expense":
            interest_expense,

        "PBT":
            pbt,

        "Opening Loss Pool":
            tax_losses_brought_forward,

        "Taxable Income After Setoff":
            taxable_income_after_setoff,

        "Closing Loss Pool":
            closing_tax_losses,

        "Tax":
            tax,

        "PAT":
            pat
    })

    # ----------------------------------
    # OUTPUT
    # ----------------------------------

    return {

        "financials": {

            "ebit":
                ebit,

            "pbt":
                pbt,

            "tax_losses_brought_forward":
                tax_losses_brought_forward,

            "taxable_income_after_setoff":
                taxable_income_after_setoff,

            "closing_tax_losses":
                closing_tax_losses,

            "tax":
                tax,

            "pat":
                pat
        },

        "dataframes": {

            "tax_df":
                tax_df
        },

        "assumption_register":
            assumptions.copy()
    }