def get_default_opex_assumptions():

    return {

        # =====================================================
        # WORKING CAPITAL
        # =====================================================

        "receivable_days": 45,
        "payable_days": 30,

        # =====================================================
        # CONSTRUCTION PERIOD
        # =====================================================

        "construction_years": 1,

        # =====================================================
        # HOUSEKEEPING
        # =====================================================

        "housekeeping_rate_per_sqft": 150,
        "housekeeping_escalation": 0.05,

        # =====================================================
        # POWER & FUEL
        # =====================================================

        "grid_power_tariff": 8.0,
        "dg_power_tariff": 20.0,
        "power_tariff_escalation": 0.05,

        # =====================================================
        # MANPOWER
        # =====================================================

        "fte_per_100_racks": 3,
        "avg_ctc_per_employee_lakh": 12,
        "manpower_escalation": 0.08,

        # Senior Management

        "senior_management_headcount": 1,
        "senior_management_ctc_lakh": 60,

        # Mid Management

        "mid_management_headcount": 2,
        "mid_management_ctc_lakh": 35,

        # Managers

        "manager_headcount": 5,
        "manager_ctc_lakh": 18,

        # Contractors

        "contractor_headcount": 10,
        "contractor_ctc_lakh": 7.25,

        # =====================================================
        # ASSET-BASED AMC
        # (MATCHES SAMPLE MODEL)
        # =====================================================

        "civil_amc_pct": 0.02,
        "electrical_amc_pct": 0.04,
        "mechanical_amc_pct": 0.08,
        "network_amc_pct": 0.08,
        "software_amc_pct": 0.12,

        # =====================================================
        # SECURITY
        # =====================================================

        "security_headcount": 15,
        "security_ctc_lakh": 4.5,

        # =====================================================
        # INSURANCE
        # =====================================================

        "insurance_pct_of_asset_value": 0.005,

        # =====================================================
        # PROPERTY TAX
        # =====================================================

        "property_tax_pct_of_asset_value": 0.01,

        # =====================================================
        # MARKETING
        # =====================================================

        "marketing_expense_crore": 1.0,
        "marketing_escalation": 0.05,
        "marketing_pct_start": 0.01,
        "marketing_pct_end": 0.0025,

        # =====================================================
        # CLOUD PARTNER FEES
        # =====================================================

        "cloud_partner_expense_crore": 0.0,

        # =====================================================
        # PENALTIES
        # =====================================================

        "penalties_crore": 0.0,

        # =====================================================
        # G&A
        # =====================================================

        "gna_pct_of_revenue": 0.03,

        # =====================================================
        # MAINTENANCE CAPEX
        # (FOR CASHFLOW ENGINE LATER)
        # =====================================================

        "maintenance_capex_rate": 0.01,

        # =====================================================
        # RAG PLACEHOLDERS
        # =====================================================

        "market_salary_multiplier": 1.0,
        "market_power_multiplier": 1.0,
        "market_maintenance_multiplier": 1.0,
        "location_cost_multiplier": 1.0,

        # =====================================================
        # LEGACY FIELDS
        # KEEP UNTIL OPEX ENGINE IS REFACTORED
        # =====================================================

        "maintenance_pct_of_revenue": 0.03,
        "network_pct_of_revenue": 0.02,
        "security_pct_of_revenue": 0.01,
        "insurance_pct_of_revenue": 0.005,
        "property_tax_pct_of_revenue": 0.01
    }