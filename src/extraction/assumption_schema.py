ASSUMPTION_DEFINITIONS = {

    "mrr_per_kw": {

        "description":
            "Monthly recurring revenue per kW",

        "unit":
            "INR_per_kw_month",

        "valid_range":
            [1000, 20000]
    },

    "lease_term_years": {

        "description":
            "Average customer lease term",

        "unit":
            "years",

        "valid_range":
            [1, 25]
    },

    "rack_density_kw": {

        "description":
            "Average rack density",

        "unit":
            "kw_per_rack",

        "valid_range":
            [1, 100]
    },

    "stabilized_utilization": {

        "description":
            "Long term stabilized utilization",

        "unit":
            "percent",

        "valid_range":
            [0, 100]
    }
}