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
    # CUMULATIVE TAXABLE PROFIT (book loss carry-forward)
    # ----------------------------------
    cumulative_pbt = []
    running = 0.0
    for p in pbt:
        running += p
        cumulative_pbt.append(running)

    # ----------------------------------
    # INCOME TAX PAYABLE
    # Tax the increase in positive cumulative PBT at the corporate rate, so
    # nothing is taxed until prior losses are absorbed.
    # ----------------------------------
    tax = []
    prev_pos = 0.0
    for i in range(years):
        cur_pos = max(cumulative_pbt[i], 0.0)
        tax.append((cur_pos - prev_pos) * tax_rate)
        prev_pos = cur_pos

    pat = [pbt[i] - tax[i] for i in range(years)]

    # ----------------------------------
    # DATAFRAME
    # ----------------------------------
    tax_df = pd.DataFrame({
        "Year":                  year_labels,
        "EBIT":                  ebit,
        "Interest Expense":      interest_expense,
        "PBT (EBT)":             pbt,
        "Cumulative Taxable Profit": cumulative_pbt,
        "Income Tax Payable":    tax,
        "PAT":                   pat,
    })

    return {

        "financials": {
            "ebit":                     ebit,
            "pbt":                      pbt,
            "cumulative_taxable_profit": cumulative_pbt,
            "tax":                      tax,
            "pat":                      pat,
        },

        "dataframes": {
            "tax_df": tax_df,
        },

        "assumption_register": assumptions.copy(),
    }
