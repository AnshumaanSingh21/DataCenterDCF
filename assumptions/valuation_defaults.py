def get_default_valuation_assumptions():

    return {

        # =====================================================
        # COST OF EQUITY  (CAPM-derived, India / INR)
        # =====================================================
        # Ke = risk-free + relevered beta x equity risk premium (+ greenfield premium)
        #
        #   Risk-free (clean)    4.85%  = 10yr G-Sec 6.70% - sovereign default spread 1.87%
        #                                (India default risk lives in the ERP, not double-counted)
        #   Equity risk premium  7.08%  = mature-market ERP 4.23% + India country risk premium 2.85%
        #   Asset (unlevered) beta 0.70 = retail-colo (speculative) digital-infra comparables
        #   Relevered beta       1.22   = 0.70 x [1 + (1-0.25) x (50/50)]  at 50% debt, 25% tax
        #   CAPM (stabilized)   13.5%   = 4.85% + 1.22 x 7.08%
        #   + greenfield premium ~1.5%  for construction / lease-up execution risk
        #   ---------------------------------------------------------------------------
        #   Cost of equity      ~= 15%
        #
        # Consistency: the 25% tax used to relever beta must match the after-tax cost
        # of debt in WACC. Refresh: G-Sec on revaluation; ERP/beta from Damodaran (Jan).
        # (Replaces the prior flat 18% guess.)
        "cost_of_equity": 0.15,

        # =====================================================
        # TERMINAL VALUE
        # =====================================================

        # "exit_multiple"  → TV = EBITDA_final × multiple  (assumes a sale at exit)
        # "gordon_growth"  → TV = FCFF_final × (1+g) / (WACC − g)  (long-term hold)
        # Base case is a long-term hold, so Gordon Growth is the primary method;
        # the exit multiple below is retained as a cross-check.
        "valuation_method": "gordon_growth",

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
