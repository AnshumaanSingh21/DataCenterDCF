def get_default_valuation_assumptions():

    return {

        # =====================================================
        # COST OF EQUITY
        # =====================================================

        # Used directly as cost of equity in WACC.
        # Typical range for Indian infra equity: 15–22%.
        "cost_of_equity": 0.18,

        # =====================================================
        # TERMINAL VALUE
        # =====================================================

        # "exit_multiple"  → TV = EBITDA_final × multiple
        # "gordon_growth"  → TV = FCFF_final × (1+g) / (WACC − g)
        "valuation_method": "exit_multiple",

        # EV / EBITDA exit multiple (used when valuation_method = "exit_multiple")
        # Indian listed data center peers trade at 18–25× EBITDA.
        # Conservative greenfield exit: 12×.
        "terminal_ev_ebitda_multiple": 12.0,

        # Long-term FCF growth rate (used when valuation_method = "gordon_growth")
        "terminal_growth_rate": 0.04,

        # =====================================================
        # HURDLE RATES
        # =====================================================

        "project_irr_hurdle": 0.15,

        "equity_irr_hurdle": 0.18,

        # Minimum DSCR covenant (breach flagged below this)
        "dscr_covenant": 1.25,
    }
