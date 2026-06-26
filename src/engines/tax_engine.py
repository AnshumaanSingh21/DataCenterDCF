import pandas as pd


def compute_tax(
    opex_output,
    depreciation_output,
    loan_output,
    assumptions
):
    """
    Simplified income tax (matches the Excel/reference model):
      EBIT  = EBITDA − book depreciation (SLM)
      PBT   = EBIT − interest
      Tax   = corporate rate applied to cumulative book PBT once it turns
              positive (book loss carry-forward). Tax in a year is the rate
              times the increase in the positive cumulative PBT.
      PAT   = PBT − tax
    """

    years = len(opex_output["metadata"]["years"])
    year_labels = opex_output["metadata"]["years"]

    ebitda           = opex_output["financials"]["ebitda"]
    book_dep         = depreciation_output["financials"]["book_depreciation"]
    interest_expense = loan_output["long_term_debt_account"]["interest_expense"]

    tax_rate = assumptions["corporate_tax_rate"]

    # ----------------------------------
    # BOOK P&L
    # ----------------------------------
    ebit = [ebitda[i] - book_dep[i] for i in range(years)]
    pbt  = [ebit[i] - interest_expense[i] for i in range(years)]

    # ----------------------------------
    # INCOME TAX with loss carry-forward pool
    # Losses accumulate in a carry-forward pool and offset future profits.
    # Tax is charged only on profit remaining after the pool is absorbed, and
    # is never negative — a loss year pays zero tax and grows the pool (no
    # phantom refund), even if it follows profitable years.
    # ----------------------------------
    tax = []
    taxable_income = []
    loss_carried_forward = []   # closing pool each year
    loss_pool = 0.0

    for i in range(years):
        p = pbt[i]
        if p < 0:
            loss_pool += -p
            taxable = 0.0
        else:
            setoff = min(loss_pool, p)
            loss_pool -= setoff
            taxable = p - setoff
        taxable_income.append(taxable)
        loss_carried_forward.append(loss_pool)
        tax.append(taxable * tax_rate)

    pat = [pbt[i] - tax[i] for i in range(years)]

    # ----------------------------------
    # DATAFRAME
    # ----------------------------------
    tax_df = pd.DataFrame({
        "Year":                  year_labels,
        "EBIT":                  ebit,
        "Interest Expense":      interest_expense,
        "PBT (EBT)":             pbt,
        "Loss Carried Forward":  loss_carried_forward,
        "Taxable Income":        taxable_income,
        "Income Tax Payable":    tax,
        "PAT":                   pat,
    })

    return {

        "financials": {
            "ebit":                  ebit,
            "pbt":                   pbt,
            "loss_carried_forward":  loss_carried_forward,
            "taxable_income":        taxable_income,
            "tax":                   tax,
            "pat":                   pat,
        },

        "dataframes": {
            "tax_df": tax_df,
        },

        "assumption_register": assumptions.copy(),
    }
