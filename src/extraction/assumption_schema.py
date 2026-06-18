ASSUMPTION_DEFINITIONS = {

    # =====================================================
    # REVENUE ENGINE MARKET ASSUMPTIONS
    # =====================================================

    "rack_price_per_rack_crore": {

        "description": (
            "Monthly colocation rack rental rate "
            "charged to tenants. Expressed in crore "
            "per rack per month (1 crore = 10,000,000 INR)."
        ),

        "unit": "crore_per_rack_per_month",

        "valid_range": [0.005, 0.030],
    },

    "utility_tariff_rs_per_kwh": {

        "description": (
            "Commercial grid electricity tariff paid "
            "by the data center operator to the utility. "
            "India commercial HT rates vary by state."
        ),

        "unit": "rs_per_kwh",

        "valid_range": [5.0, 14.0],
    },

    "power_markup_rs_per_kwh": {

        "description": (
            "Premium charged to tenants over and above "
            "the utility tariff per kWh of facility load. "
            "Represents the operator's power margin."
        ),

        "unit": "rs_per_kwh",

        "valid_range": [0.5, 5.0],
    },

    "otc_price_per_new_rack_crore": {

        "description": (
            "One-time setup or installation fee charged "
            "per new rack at time of deployment. "
            "Expressed in crore per rack."
        ),

        "unit": "crore_per_rack",

        "valid_range": [0.005, 0.100],
    },

    "rack_price_escalation": {

        "description": (
            "Annual escalation rate applied to rack "
            "rental pricing. Expressed as a decimal "
            "(e.g. 0.05 = 5% per year)."
        ),

        "unit": "decimal_annual_rate",

        "valid_range": [0.02, 0.10],
    },

    "power_tariff_escalation": {

        "description": (
            "Annual escalation rate applied to power "
            "tariffs. Expressed as a decimal "
            "(e.g. 0.05 = 5% per year)."
        ),

        "unit": "decimal_annual_rate",

        "valid_range": [0.02, 0.10],
    },

    # =====================================================
    # LEGACY (kept for backward compatibility)
    # =====================================================

    "mrr_per_kw": {

        "description": "Monthly recurring revenue per kW",

        "unit": "INR_per_kw_month",

        "valid_range": [1000, 20000],
    },

    "lease_term_years": {

        "description": "Average customer lease term",

        "unit": "years",

        "valid_range": [1, 25],
    },

    "rack_density_kw": {

        "description": "Average rack density",

        "unit": "kw_per_rack",

        "valid_range": [1, 100],
    },

    "stabilized_utilization": {

        "description": "Long term stabilized utilization",

        "unit": "percent",

        "valid_range": [0, 100],
    },
}
