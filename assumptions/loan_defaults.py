def get_default_loan_assumptions():

    return {

        # =====================================
        # CAPITAL STRUCTURE
        # =====================================

        "debt_pct": 0.50,

        "equity_pct": 0.50,

        # =====================================
        # LOAN TERMS
        # =====================================

        "interest_rate": 0.10,

        "loan_tenure_years": 10,

        "moratorium_years": 3,

        # =====================================
        # REPAYMENT
        # =====================================

        "repayment_type": "equal_principal",

        # =====================================
        # FEES
        # =====================================

        "processing_fee_pct": 0.01,

        # =====================================
        # IDC
        # =====================================

        "capitalize_interest": True,

        # =====================================
        # FUTURE RAG INPUTS
        # =====================================

        "market_interest_rate": 0.10,

        "credit_spread": 0.00,

        "location_risk_premium": 0.00
    }