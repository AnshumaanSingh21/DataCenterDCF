ASSUMPTION_DEFINITIONS = {

    # =====================================================
    # REVENUE ENGINE MARKET ASSUMPTIONS
    # =====================================================

    "rack_price_per_rack_crore": {

        "description": (
            "Monthly colocation rack rental rate charged to tenants. "
            "Pricing depends on TENANT TYPE, not just facility size. "
            "Retail colo (multiple enterprise tenants): ₹50k-80k/rack/month. "
            "Wholesale/hyperscale (single large tenant, 1MW+): ₹30k-45k/rack/month. "
            "Use the facility type stated in the prompt to pick the right bracket. "
            "Expressed in crore per rack per month (1 crore = 10,000,000 INR)."
        ),

        "unit": "crore_per_rack_per_month",

        "valid_range": [0.003, 0.030],
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
    # CAPEX BENCHMARKS
    # =====================================================

    "civil_capex_cr_per_mw": {

        "description": (
            "Civil and structural construction cost per MW of IT load capacity. "
            "Includes land development, building shell, raised floor, and fit-out. "
            "Expressed in INR crore per MW."
        ),

        "unit": "crore_per_mw",

        "valid_range": [5.0, 40.0],
    },

    "electrical_capex_cr_per_mw": {

        "description": (
            "Electrical infrastructure cost per MW of IT load capacity. "
            "Includes HV/LV switchgear, UPS, transformers, DG sets, and cabling. "
            "Expressed in INR crore per MW."
        ),

        "unit": "crore_per_mw",

        "valid_range": [8.0, 50.0],
    },

    "mechanical_capex_cr_per_mw": {

        "description": (
            "Mechanical and cooling infrastructure cost per MW of IT load capacity. "
            "Includes chillers, CRAC/CRAH units, cooling towers, and piping. "
            "Expressed in INR crore per MW."
        ),

        "unit": "crore_per_mw",

        "valid_range": [5.0, 35.0],
    },

    "it_hardware_cr_per_rack": {

        "description": (
            "Operator-owned IT overhead cost per rack in a COLOCATION data center. "
            "In colo, tenants own servers/storage — the operator only provides "
            "shared infrastructure: patch panels, PDUs, KVM, DCIM hardware. "
            "This is NOT the cost of tenant servers. Typical range ₹0.01-0.05 Cr/rack. "
            "Do NOT use hyperscaler or enterprise build costs here. "
            "Expressed in INR crore per rack."
        ),

        "unit": "crore_per_rack",

        "valid_range": [0.005, 0.10],
    },

    "network_capex_cr_per_rack": {

        "description": (
            "Network infrastructure cost per rack. "
            "Includes spine-leaf switching, patch panels, and fiber distribution. "
            "Expressed in INR crore per rack."
        ),

        "unit": "crore_per_rack",

        "valid_range": [0.01, 0.5],
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
