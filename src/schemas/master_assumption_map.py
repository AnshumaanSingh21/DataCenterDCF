INPUTS = {

    "location",

    "total_racks",

    "facility_type"
}


ENGINEERING_DEFAULTS = {

    "kw_per_rack",

    "pue",

    "availability_sla_pct",

    "lease_up_curve"
}


MARKET_ASSUMPTIONS = {

    "rack_price_per_rack",

    "cross_connect_fee",

    "cross_connect_penetration",

    "utility_tariff_rs_per_kwh",

    "tenant_power_rate_rs_per_kwh",

    "managed_services_penetration",

    "managed_service_price_per_rack",

    "average_contract_term_years",

    "annual_price_escalation"
}


FINANCIAL_POLICY_ASSUMPTIONS = {

    "tax_rate",

    "bad_debt_pct",

    "marketing_expense_pct",

    "sga_pct",

    "renewal_probability"
}


DERIVED_VARIABLES = {

    "it_load_kw",

    "facility_load_kw",

    "occupied_racks",

    "occupied_kw",

    "sellable_capacity"
}