MARKET_ASSUMPTIONS = [

    # Revenue
    "rack_price_per_rack_crore",
    "utility_tariff_rs_per_kwh",
    "power_markup_rs_per_kwh",
    "otc_price_per_new_rack_crore",
    "rack_price_escalation",
    "power_tariff_escalation",

    # CapEx benchmarks
    "civil_capex_cr_per_mw",
    "electrical_capex_cr_per_mw",
    "mechanical_capex_cr_per_mw",
    "it_hardware_cr_per_rack",
    "network_capex_cr_per_rack",

]

# TTL (days) per assumption — how long a cached value stays valid
ASSUMPTION_TTL = {
    "rack_price_per_rack_crore":    90,
    "power_markup_rs_per_kwh":      90,
    "utility_tariff_rs_per_kwh":    180,
    "otc_price_per_new_rack_crore": 90,
    "rack_price_escalation":        365,
    "power_tariff_escalation":      365,
    "civil_capex_cr_per_mw":        365,
    "electrical_capex_cr_per_mw":   365,
    "mechanical_capex_cr_per_mw":   365,
    "it_hardware_cr_per_rack":      365,
    "network_capex_cr_per_rack":    365,
}
