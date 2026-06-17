import numpy as np
import pandas as pd
import numpy_financial as npf


def compute_cashflow(
    opex_output,
    capex_output,
    depreciation_output,
    loan_output,
    tax_output,
    working_capital_output,
    
):

    years = (
        opex_output["metadata"]["years"]
    )

    # ----------------------------------
    # INPUTS
    # ----------------------------------

    ebitda = (
        opex_output["financials"]
        ["ebitda"]
    )

    depreciation = (
        depreciation_output["financials"]
        ["total_depreciation"]
    )

    capex = (
        capex_output["financials"]
        ["total_capex"]
    )

    # Pull corporate tax rate from assumptions used by tax engine (fallback to 25%)
    tax_rate = (
        tax_output.get("assumption_register", {}).get("corporate_tax_rate", 0.25)
    )
    
    ebit = (
        tax_output["financials"]
        ["ebit"]
    )

    pat = (
        tax_output["financials"]
        ["pat"]
    )

    tax = (
        tax_output["financials"]
        ["tax"]
    )

    change_in_wc = (
        working_capital_output["financials"]
        ["change_in_working_capital"]
    )

    debt_drawdown = (
    loan_output[
        "long_term_debt_account"
    ]["drawdown"]
    )

    interest = (
        loan_output[
            "long_term_debt_account"
        ]["interest_expense"]
    )

    principal = (
        loan_output[
            "long_term_debt_account"
        ]["principal_repayment"]
    )

    # ----------------------------------
    # NOPAT
    # ----------------------------------

    nopat = [

    ebit[i]
    * (1 - tax_rate)

    for i in range(len(years))
    ]
    # ----------------------------------
    # FCFF
    # ----------------------------------

    fcff = []

    for i in range(len(years)):

        fcff.append(

            nopat[i]

            + depreciation[i]

            - capex[i]

            - change_in_wc[i]
        )

    # ----------------------------------
    # FCFE
    # ----------------------------------

    fcfe = []

    for i in range(len(years)):

        fcfe.append(

            pat[i]

            + depreciation[i]

            - capex[i]

            - change_in_wc[i]

            + debt_drawdown[i]

            - principal[i]
        )

    # ----------------------------------
    # MAINTENANCE CAPEX (APPLIED TO CFADS FROM YEAR 5 ONWARDS)
    # ----------------------------------

    # Base = cumulative depreciable capex excluding land
    cumulative_capex = (
        capex_output["financials"]["cumulative_capex"]
    )

    land_cost = (
        capex_output["site_sizing"]["land_cost_crore"]
    )

    maintenance_rate = (
        opex_output.get("assumption_register", {}).get("maintenance_capex_rate", 0)
    )

    maintenance_capex = []

    for i in range(len(years)):

        base = max(cumulative_capex[i] - land_cost, 0)

        # apply from Year 5 onwards (index 4)
        if i >= 4:
            maintenance_capex.append(base * maintenance_rate)
        else:
            maintenance_capex.append(0)

    # ----------------------------------
    # CFADS
    # ----------------------------------

    cfads = []

    for i in range(len(years)):

        cfads.append(

            ebitda[i]

            - tax[i]

            - change_in_wc[i]

            - maintenance_capex[i]
        )

    # ----------------------------------
    # DEBT SERVICE
    # ----------------------------------

    debt_service = []

    for i in range(len(years)):

        debt_service.append(

            interest[i]

            + principal[i]
        )

    # ----------------------------------
    # DSCR
    # ----------------------------------

    dscr = []

    for i in range(len(years)):

        if debt_service[i] > 0:

            dscr.append(

                cfads[i]
                / debt_service[i]
            )

        else:

            dscr.append(None)

    # ----------------------------------
    # IRR
    # ----------------------------------

    try:

        project_irr = npf.irr(fcff)

    except:

        project_irr = None

    try:

        equity_irr = npf.irr(fcfe)

    except:

        equity_irr = None

    # ----------------------------------
    # DATAFRAME
    # ----------------------------------

    cashflow_df = pd.DataFrame({

        "Year":
            years,

        "NOPAT":
            nopat,

        "Capex":
            capex,

        "Depreciation":
            depreciation,

        "Change in WC":
            change_in_wc,

        "FCFF":
            fcff,

        "FCFE":
            fcfe,

        "CFADS":
            cfads,

        "Debt Service":
            debt_service,

        "DSCR":
            dscr
    })

    # ----------------------------------
    # OUTPUT
    # ----------------------------------

    return {

        "financials": {

            "nopat":
                nopat,

            "fcff":
                fcff,

            "fcfe":
                fcfe,

            "cfads":
                cfads,

            "debt_service":
                debt_service,

            "dscr":
                dscr,

            "project_irr":
                project_irr,

            "equity_irr":
                equity_irr
        },

        "dataframes": {

            "cashflow_df":
                cashflow_df
        }
    }