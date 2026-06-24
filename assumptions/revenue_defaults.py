from copy import deepcopy


DEFAULT_REVENUE_ASSUMPTIONS = {

    # =====================================================
    # GENERAL
    # =====================================================

    "lease_up_curve": [
        0.10,
        0.16,
        0.24,
        0.33,
        0.42,
        0.51,
        0.60,
        0.69,
        0.78,
        0.87,
    ],

    "pue": 1.6,

    "dot_share_pct": 0.0,

    "crore_divisor": 10_000_000,

    # =====================================================
    # FACILITY CHARACTERISTICS
    # =====================================================

    "power_per_rack_kw": 6.0,

    "rack_density_category": "standard",

    "availability_sla_pct": 99.99,

    # =====================================================
    # RECURRING COLOCATION REVENUE
    # =====================================================

    # Rs 50,000/rack/month space charge (power billed separately).
    # All-in to tenant ~Rs 86,000-93,000/month (space + 4.5 kW metered power).
    # Market range Mumbai Tier III greenfield 2026: Rs 65,000-100,000/month all-in.
    "rack_price_per_rack_crore": 0.0055,

    "rack_price_escalation": 0.05,

    "rack_realization_pct": 1.0,

    "rack_discount_pct": 0.0,

    # =====================================================
    # ONE TIME SETUP REVENUE
    # =====================================================

    # Rs 30,000 one-time per rack (~2.5 months rack rent). Market: Rs 10,000-50,000.
    "otc_price_per_new_rack_crore": 0.0003,

    "otc_price_escalation": 0.05,

    "otc_realization_pct": 1.0,

    "cross_connect_fee_crore": 0.0,

    "migration_fee_crore": 0.0,

    # =====================================================
    # POWER REVENUE
    # =====================================================

    "utility_tariff_rs_per_kwh": 8.0,

    "tenant_power_rate_rs_per_kwh": 9.5,

    "power_markup_rs_per_kwh": 1.5,

    "power_tariff_escalation": 0.05,

    "power_realization_pct": 1.0,

    "renewable_energy_premium_rs_per_kwh": 0.0,

    # =====================================================
    # SEATS / WORKSPACE REVENUE
    # =====================================================

    "seats_per_rack": 0.01,

    # Rs 10,000/seat/month for dedicated DC workspace (Mumbai 2024).
    "seat_price_per_seat_crore": 0.001,

    "seat_price_escalation": 0.05,

    "seat_realization_pct": 1.0,

    # =====================================================
    # MANAGED SERVICES REVENUE
    # =====================================================

    "managed_services_penetration": 0.0,

    # Rs 20,000/rack/month for managed services bundle (NOC monitoring, OS patching, etc.).
    "managed_service_price_per_rack_crore": 0.002,

    "managed_service_escalation": 0.05,

    "managed_service_realization_pct": 1.0,

    # =====================================================
    # NETWORK SERVICES (FUTURE)
    # =====================================================

    "ip_transit_revenue_crore": 0.0,

    "network_service_penetration": 0.0,

    "network_service_escalation": 0.05,

    # =====================================================
    # CLOUD CONNECTIVITY (FUTURE)
    # =====================================================

    "cloud_connect_revenue_crore": 0.0,

    "cloud_connect_penetration": 0.0,

    "cloud_connect_escalation": 0.05,

    # =====================================================
    # AI / HPC PREMIUM (FUTURE)
    # =====================================================

    "ai_density_premium_pct": 0.0,

    "gpu_hosting_revenue_crore": 0.0,
    # =====================================================
    # CROSS CONNECT REVENUE
    # =====================================================

    "cross_connect_penetration": 0.0,

    "cross_connect_fee_per_connection_crore": 0.0,

    "cross_connect_escalation": 0.05,

    # =====================================================
    # REMOTE HANDS REVENUE
    # =====================================================

    "remote_hands_penetration": 0.0,

    "remote_hands_revenue_per_rack_crore": 0.0,

    "remote_hands_escalation": 0.05,

    # =====================================================
    # PROFESSIONAL SERVICES REVENUE
    # =====================================================

    "professional_services_penetration": 0.0,

    "professional_services_revenue_per_rack_crore": 0.0,

    "professional_services_escalation": 0.05,

    # =====================================================
    # DISASTER RECOVERY SERVICES
    # =====================================================

    "dr_services_penetration": 0.0,

    "dr_services_revenue_per_rack_crore": 0.0,

    "dr_services_escalation": 0.05,

    # =====================================================
    # CUSTOMER BEHAVIOUR
    # =====================================================

    "customer_churn_pct": 0.0,

    "customer_expansion_pct": 0.0,

    # =====================================================
    # CONTRACT STRUCTURE
    # =====================================================

    "average_contract_term_years": 3,

    "renewal_probability": 0.90,

    # =====================================================
    # CAPACITY MANAGEMENT
    # =====================================================

    "reserved_capacity_pct": 0.0,

    "sellable_capacity_pct": 1.0,

    # =====================================================
    # RAG PLACEHOLDERS
    # =====================================================

    "market_rack_rate_multiplier": 1.0,

    "market_power_rate_multiplier": 1.0,

    "market_demand_multiplier": 1.0,

    "location_pricing_multiplier": 1.0,

    # =====================================================
    # LEGACY FIELDS
    # KEEP UNTIL REVENUE ENGINE IS REFACTORED
    # =====================================================

    "kw_per_rack": 6.0,

    "rack_mrc_crore": 0.0055,

    "rack_mrc_escalation": 0.05,

    "otc_fee_crore": 0.0003,

    "otc_fee_escalation": 0.05,

    "seat_mrc_crore": 0.001,

    "seat_mrc_escalation": 0.05,

    "seats_per_rack_ratio": 0.01,

    "managed_rack_mrc_crore": 0.002,

    "managed_rack_escalation": 0.05,
}


FACILITY_TYPE_OVERRIDES = {

    "retail_colo": {

        "kw_per_rack": 4.5,

        "power_per_rack_kw": 4.5,

        "managed_services_penetration": 0.0,
    },

    "wholesale": {

        "kw_per_rack": 8.0,

        "power_per_rack_kw": 8.0,

        "managed_services_penetration": 0.0,
    },

    "ai_hpc": {

        "kw_per_rack": 40.0,

        "power_per_rack_kw": 40.0,

        "managed_services_penetration": 0.0,
    },

    "hyperscale": {

        "kw_per_rack": 12.0,

        "power_per_rack_kw": 12.0,

        "managed_services_penetration": 0.0,
    }
}


def get_default_revenue_assumptions():

    return deepcopy(
        DEFAULT_REVENUE_ASSUMPTIONS
    )