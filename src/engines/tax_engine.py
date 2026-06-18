import pandas as pd


def compute_tax(
    opex_output,
    depreciation_output,
    loan_output,
    assumptions
):

    years = len(opex_output["metadata"]["years"])
    year_labels = opex_output["metadata"]["years"]

    ebitda           = opex_output["financials"]["ebitda"]
    book_dep         = depreciation_output["financials"]["book_depreciation"]
    tax_dep          = depreciation_output["financials"]["tax_depreciation"]
    interest_expense = loan_output["long_term_debt_account"]["interest_expense"]

    tax_rate = assumptions["corporate_tax_rate"]
    mat_rate = assumptions.get("minimum_alternate_tax", 0.15)

    # ----------------------------------
    # BOOK P&L (Companies Act SLM dep)
    # EBIT and PBT here feed the P&L
    # statement and MAT base.
    # ----------------------------------

    ebit = [ebitda[i] - book_dep[i] for i in range(years)]
    pbt  = [ebit[i] - interest_expense[i] for i in range(years)]

    # ----------------------------------
    # TAX P&L (IT Act WDV dep)
    # Taxable profit before loss setoff.
    # Higher WDV dep → lower taxable profit
    # in early years vs book PBT.
    # ----------------------------------

    tax_ebit = [ebitda[i] - tax_dep[i] for i in range(years)]
    tax_pbt  = [tax_ebit[i] - interest_expense[i] for i in range(years)]

    # ----------------------------------
    # CORPORATE TAX with loss carry-fwd
    # Loss pool tracks tax PBT losses
    # (not book losses) — 8-yr limit
    # simplified to full projection horizon.
    # ----------------------------------

    corporate_tax               = []
    taxable_income_after_setoff = []
    tax_losses_bf               = []
    closing_tax_losses          = []

    loss_pool = 0.0

    for i in range(years):
        opening_pool = loss_pool
        tpbt = tax_pbt[i]

        if tpbt < 0:
            taxable_income = 0.0
            loss_pool += abs(tpbt)
            ct = 0.0
        else:
            setoff = min(loss_pool, tpbt)
            loss_pool -= setoff
            taxable_income = tpbt - setoff
            ct = taxable_income * tax_rate

        corporate_tax.append(ct)
        taxable_income_after_setoff.append(taxable_income)
        tax_losses_bf.append(opening_pool)
        closing_tax_losses.append(loss_pool)

    # ----------------------------------
    # MAT — Minimum Alternate Tax
    # 15% of book PBT (when positive).
    # Applies even if CT = 0 due to loss
    # setoff or WDV deductions.
    # ----------------------------------

    mat = [
        max(pbt[i], 0) * mat_rate
        for i in range(years)
    ]

    # ----------------------------------
    # MAT CREDIT CARRY-FORWARD
    # When MAT > CT: earn credit = MAT - CT
    # When CT > MAT: utilize credit (reduces
    # actual cash tax) capped at CT - MAT.
    # Credit expires in 15 years (simplified:
    # tracked over projection horizon).
    # ----------------------------------

    mat_credit_pool     = []
    mat_credit_earned   = []
    mat_credit_utilized = []
    effective_tax       = []

    credit_pool = 0.0

    for i in range(years):
        ct  = corporate_tax[i]
        mat_i = mat[i]
        tax_payable = max(ct, mat_i)

        if mat_i > ct:
            earned    = mat_i - ct
            utilized  = 0.0
            credit_pool += earned
            cash_tax  = mat_i
        else:
            earned    = 0.0
            utilized  = min(ct - mat_i, credit_pool)
            credit_pool -= utilized
            cash_tax  = ct - utilized

        mat_credit_earned.append(earned)
        mat_credit_utilized.append(utilized)
        mat_credit_pool.append(credit_pool)
        effective_tax.append(cash_tax)

    # ----------------------------------
    # PAT uses book PBT − effective tax
    # ----------------------------------

    pat = [pbt[i] - effective_tax[i] for i in range(years)]

    # ----------------------------------
    # DATAFRAMES
    # ----------------------------------

    tax_df = pd.DataFrame({
        "Year":                        year_labels,
        "EBITDA":                      ebitda,
        "Book Dep (SLM)":              book_dep,
        "Tax Dep (WDV)":               tax_dep,
        "EBIT (Book)":                 ebit,
        "Tax EBIT (WDV)":              tax_ebit,
        "Interest Expense":            interest_expense,
        "PBT (Book)":                  pbt,
        "Tax PBT (WDV)":               tax_pbt,
        "Opening Loss Pool":           tax_losses_bf,
        "Taxable Income After Setoff": taxable_income_after_setoff,
        "Closing Loss Pool":           closing_tax_losses,
        "Corporate Tax":               corporate_tax,
        "MAT (15% of Book PBT)":       mat,
        "MAT Credit Earned":           mat_credit_earned,
        "MAT Credit Utilized":         mat_credit_utilized,
        "MAT Credit Pool":             mat_credit_pool,
        "Effective Tax (Cash)":        effective_tax,
        "PAT":                         pat,
    })

    return {

        "financials": {
            "ebit":                        ebit,
            "pbt":                         pbt,
            "tax_pbt":                     tax_pbt,
            "taxable_income_after_setoff": taxable_income_after_setoff,
            "tax_losses_brought_forward":  tax_losses_bf,
            "closing_tax_losses":          closing_tax_losses,
            "corporate_tax":               corporate_tax,
            "mat":                         mat,
            "mat_credit_pool":             mat_credit_pool,
            "mat_credit_earned":           mat_credit_earned,
            "mat_credit_utilized":         mat_credit_utilized,
            "tax":                         effective_tax,   # cash tax — used by cashflow engine
            "pat":                         pat,
        },

        "dataframes": {
            "tax_df": tax_df,
        },

        "assumption_register": assumptions.copy(),
    }
