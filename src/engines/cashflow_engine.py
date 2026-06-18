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
    valuation_assumptions=None,
):

    if valuation_assumptions is None:
        valuation_assumptions = {}

    val = valuation_assumptions

    years = opex_output["metadata"]["years"]
    n = len(years)

    # ----------------------------------
    # PULL INPUTS FROM UPSTREAM ENGINES
    # ----------------------------------

    net_revenue   = opex_output["financials"]["net_revenue"]
    total_opex    = opex_output["financials"]["total_opex"]
    ebitda        = opex_output["financials"]["ebitda"]
    ebitda_margin = opex_output["financials"]["ebitda_margin"]

    depreciation  = depreciation_output["financials"]["total_depreciation"]

    ebit          = tax_output["financials"]["ebit"]
    pbt           = tax_output["financials"]["pbt"]
    tax           = tax_output["financials"]["tax"]
    pat           = tax_output["financials"]["pat"]

    interest      = loan_output["long_term_debt_account"]["interest_expense"]
    principal     = loan_output["long_term_debt_account"]["principal_repayment"]
    debt_drawdown = loan_output["long_term_debt_account"]["drawdown"]
    closing_debt  = loan_output["long_term_debt_account"]["closing_balance"]
    equity_funding = loan_output["capital_structure"]["equity_funding"]

    capex         = capex_output["financials"]["total_capex"]
    cumulative_capex = capex_output["financials"]["cumulative_capex"]
    land_cost     = capex_output["site_sizing"]["land_cost_crore"]

    change_in_wc  = working_capital_output["financials"]["change_in_working_capital"]

    tax_rate      = tax_output.get(
        "assumption_register", {}
    ).get("corporate_tax_rate", 0.25)

    loan_reg      = loan_output.get("assumption_register", {})
    debt_pct      = loan_reg.get("debt_pct", 0.60)
    equity_pct    = loan_reg.get("equity_pct", 0.40)
    interest_rate = loan_reg.get("interest_rate", 0.10)

    maint_rate    = opex_output.get(
        "assumption_register", {}
    ).get("maintenance_capex_rate", 0.01)

    # ----------------------------------
    # NOPAT
    # ----------------------------------

    nopat = [
        ebit[i] * (1 - tax_rate)
        for i in range(n)
    ]

    # ----------------------------------
    # MAINTENANCE CAPEX (from Year 5)
    # ----------------------------------

    maintenance_capex = [
        max(cumulative_capex[i] - land_cost, 0) * maint_rate
        if i >= 4 else 0
        for i in range(n)
    ]

    # ----------------------------------
    # FCFF
    # NOPAT + Depreciation − CapEx − ΔWC
    # ----------------------------------

    fcff = [
        nopat[i]
        + depreciation[i]
        - capex[i]
        - change_in_wc[i]
        for i in range(n)
    ]

    # ----------------------------------
    # FCFE
    # PAT + Depreciation − CapEx − ΔWC
    # + Debt Drawdown − Principal Repaid
    # ----------------------------------

    fcfe = [
        pat[i]
        + depreciation[i]
        - capex[i]
        - change_in_wc[i]
        + debt_drawdown[i]
        - principal[i]
        for i in range(n)
    ]

    # ----------------------------------
    # CFADS
    # EBITDA − Tax − ΔWC − Maint Capex
    # ----------------------------------

    cfads = [
        ebitda[i]
        - tax[i]
        - change_in_wc[i]
        - maintenance_capex[i]
        for i in range(n)
    ]

    # ----------------------------------
    # DEBT SERVICE & DSCR
    # ----------------------------------

    debt_service = [
        interest[i] + principal[i]
        for i in range(n)
    ]

    dscr = [
        cfads[i] / debt_service[i]
        if debt_service[i] > 0 else None
        for i in range(n)
    ]

    # ----------------------------------
    # TERMINAL VALUE
    # ----------------------------------

    method = val.get("valuation_method", "exit_multiple")

    # Compute terminal value early (needed for IRR)
    cost_of_equity    = val.get("cost_of_equity", 0.18)
    cost_of_debt_post = interest_rate * (1 - tax_rate)
    _wacc_early = cost_of_equity * equity_pct + cost_of_debt_post * debt_pct

    if method == "gordon_growth":
        g = val.get("terminal_growth_rate", 0.04)
        terminal_value = (
            fcff[-1] * (1 + g) / (_wacc_early - g)
            if _wacc_early > g else 0.0
        )
    else:
        multiple = val.get("terminal_ev_ebitda_multiple", 12.0)
        terminal_value = ebitda[-1] * multiple

    # Terminal equity value = enterprise value at exit minus residual debt
    equity_terminal_value = max(terminal_value - closing_debt[-1], 0.0)

    fcff_with_tv = fcff.copy()
    fcff_with_tv[-1] = fcff_with_tv[-1] + terminal_value

    fcfe_with_tv = fcfe.copy()
    fcfe_with_tv[-1] = fcfe_with_tv[-1] + equity_terminal_value

    # ----------------------------------
    # IRR
    # IRR computed on terminal-value-inclusive series to match NPV convention.
    # ----------------------------------

    try:
        project_irr = float(npf.irr(fcff_with_tv))
    except Exception:
        project_irr = None

    try:
        equity_irr = float(npf.irr(fcfe_with_tv))
    except Exception:
        equity_irr = None

    # ----------------------------------
    # WACC
    # ----------------------------------

    wacc = _wacc_early  # already computed above

    # ----------------------------------
    # NPV
    # Discount FCFF at WACC; terminal value already in fcff_with_tv.
    # Year-end convention: FCFF[0] at t=1.
    # ----------------------------------

    try:
        npv = float(npf.npv(wacc, fcff_with_tv))
    except Exception:
        npv = None

    # ----------------------------------
    # CUMULATIVE FCFF & PAYBACK
    # ----------------------------------

    cumulative_fcff = []
    running = 0.0
    for f in fcff:
        running += f
        cumulative_fcff.append(running)

    payback_year = None
    for i in range(n):
        if cumulative_fcff[i] >= 0:
            if i == 0:
                payback_year = years[i]
            else:
                # linear interpolation within the year
                prev = cumulative_fcff[i - 1]
                curr = cumulative_fcff[i]
                frac = abs(prev) / (abs(prev) + curr)
                payback_year = round(
                    years[i - 1] + frac, 1
                )
            break

    discounted_cumulative = []
    running_disc = 0.0
    discounted_payback_year = None
    for i in range(n):
        disc_fcff = fcff[i] / (1 + wacc) ** (i + 1)
        running_disc += disc_fcff
        discounted_cumulative.append(running_disc)
        if running_disc >= 0 and discounted_payback_year is None:
            if i == 0:
                discounted_payback_year = years[i]
            else:
                prev = discounted_cumulative[i - 1]
                curr = discounted_cumulative[i]
                frac = abs(prev) / (abs(prev) + curr)
                discounted_payback_year = round(
                    years[i - 1] + frac, 1
                )

    # ----------------------------------
    # EQUITY SCHEDULE & MOIC
    # ----------------------------------

    cumulative_equity = []
    running_eq = 0.0
    for e in equity_funding:
        running_eq += e
        cumulative_equity.append(running_eq)

    total_equity_invested = sum(equity_funding)
    # Include terminal equity value in returns (MOIC is total-return-inclusive)
    total_equity_returned = sum(
        f for f in fcfe_with_tv if f > 0
    )

    moic = (
        round(total_equity_returned / total_equity_invested, 2)
        if total_equity_invested > 0 else None
    )

    # ----------------------------------
    # DEBT METRICS
    # ----------------------------------

    icr = [
        ebitda[i] / interest[i]
        if interest[i] > 0 else None
        for i in range(n)
    ]

    leverage_ratio = [
        closing_debt[i] / ebitda[i]
        if ebitda[i] > 0 else None
        for i in range(n)
    ]

    dscr_covenant = val.get("dscr_covenant", 1.25)

    dscr_min = min(
        d for d in dscr if d is not None
    )

    dscr_breaches = [
        {"year": years[i], "dscr": round(dscr[i], 2)}
        for i in range(n)
        if dscr[i] is not None and dscr[i] < dscr_covenant
    ]

    # ----------------------------------
    # SOURCES & USES (per phase)
    # ----------------------------------

    sources_and_uses = []

    for tranche in loan_output.get("tranches", []):
        dy = tranche["draw_year"]
        capex_amt = capex[dy]
        debt_amt  = tranche["loan_amount"]
        eq_amt    = equity_funding[dy]

        sources_and_uses.append({
            "year":        years[dy],
            "total_capex": round(capex_amt, 2),
            "debt":        round(debt_amt, 2),
            "equity":      round(eq_amt, 2),
        })

    total_su = {
        "year":        "Total",
        "total_capex": round(sum(capex), 2),
        "debt":        round(sum(debt_drawdown), 2),
        "equity":      round(sum(equity_funding), 2),
    }
    sources_and_uses.append(total_su)

    # ----------------------------------
    # DATAFRAMES
    # ----------------------------------

    pnl_df = pd.DataFrame({
        "Year":             years,
        "Net Revenue":      net_revenue,
        "Total OpEx":       total_opex,
        "EBITDA":           ebitda,
        "EBITDA Margin":    [round(x, 3) for x in ebitda_margin],
        "Depreciation":     depreciation,
        "EBIT":             ebit,
        "Interest Expense": interest,
        "PBT":              pbt,
        "Tax":              tax,
        "PAT":              pat,
    })

    cashflow_df = pd.DataFrame({
        "Year":            years,
        "NOPAT":           nopat,
        "Capex":           capex,
        "Depreciation":    depreciation,
        "Change in WC":    change_in_wc,
        "FCFF":            fcff,
        "Cumul FCFF":      cumulative_fcff,
        "FCFE":            fcfe,
        "CFADS":           cfads,
        "Debt Service":    debt_service,
        "DSCR":            dscr,
    })

    debt_df = pd.DataFrame({
        "Year":      years,
        "EBITDA":    ebitda,
        "Interest":  interest,
        "ICR":       icr,
        "Closing Debt": closing_debt,
        "Leverage":  leverage_ratio,
        "DSCR":      dscr,
    })

    su_df = pd.DataFrame(sources_and_uses)

    equity_df = pd.DataFrame({
        "Year":            years,
        "Equity Injected": equity_funding,
        "Cumul Equity":    cumulative_equity,
        "FCFE":            fcfe,
    })

    # ----------------------------------
    # OUTPUT
    # ----------------------------------

    return {

        "metadata": {
            "years": years,
            "wacc":  round(wacc, 4),
        },

        "pnl": {
            "net_revenue":      net_revenue,
            "total_opex":       total_opex,
            "ebitda":           ebitda,
            "ebitda_margin":    ebitda_margin,
            "depreciation":     depreciation,
            "ebit":             ebit,
            "interest_expense": interest,
            "pbt":              pbt,
            "tax":              tax,
            "pat":              pat,
        },

        "cashflows": {
            "nopat":            nopat,
            "capex":            capex,
            "maintenance_capex": maintenance_capex,
            "change_in_wc":     change_in_wc,
            "fcff":             fcff,
            "cumulative_fcff":  cumulative_fcff,
            "fcfe":             fcfe,
            "cfads":            cfads,
            "debt_service":     debt_service,
            "dscr":             dscr,
        },

        "valuation": {
            "wacc":                    round(wacc, 4),
            "cost_of_equity":          cost_of_equity,
            "cost_of_debt_post_tax":   round(cost_of_debt_post, 4),
            "terminal_value":          round(terminal_value, 2),
            "terminal_method":         method,
            "npv":                     round(npv, 2) if npv else None,
            "project_irr":             project_irr,
            "equity_irr":              equity_irr,
            "payback_year":            payback_year,
            "discounted_payback_year": discounted_payback_year,
            "moic":                    moic,
        },

        "debt_metrics": {
            "icr":              icr,
            "leverage_ratio":   leverage_ratio,
            "dscr":             dscr,
            "dscr_min":         round(dscr_min, 2),
            "dscr_covenant":    dscr_covenant,
            "dscr_breaches":    dscr_breaches,
        },

        "equity": {
            "equity_funding":          equity_funding,
            "cumulative_equity":       cumulative_equity,
            "total_equity_invested":   round(total_equity_invested, 2),
            "total_equity_returned":   round(total_equity_returned, 2),
            "moic":                    moic,
        },

        "sources_and_uses": sources_and_uses,

        # investor_metrics — alias for external runners that expect this key
        "investor_metrics": {
            "project_irr": project_irr,
            "equity_irr":  equity_irr,
            "project_npv": round(npv, 2) if npv else None,
            "equity_npv":  round(npv - sum(equity_funding), 2) if npv else None,
            "terminal_value": round(terminal_value, 2),
            "moic":        moic,
        },

        # Legacy key — kept for backward compat with existing runners
        "financials": {
            "nopat":       nopat,
            "fcff":        fcff,
            "fcfe":        fcfe,
            "cfads":       cfads,
            "debt_service": debt_service,
            "dscr":        dscr,
            "project_irr": project_irr,
            "equity_irr":  equity_irr,
        },

        "dataframes": {
            "pnl_df":        pnl_df,
            "cashflow_df":   cashflow_df,
            "debt_df":       debt_df,
            "su_df":         su_df,
            "equity_df":     equity_df,
        },
    }
