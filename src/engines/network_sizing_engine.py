import math


def compute_network_sizing(
    total_racks,
    assumptions
):

    contingency_pct = assumptions[
        "network_contingency_pct"
    ]

    # ----------------------------------
    # QUANTITIES
    # ----------------------------------

    dmz_switch_count = math.ceil(
        total_racks / 10
    ) * assumptions[
        "dmz_switches_per_10_racks"
    ]

    core_switch_count = math.ceil(
        total_racks / 20
    ) * assumptions[
        "core_switches_per_20_racks"
    ]

    server_switch_count = math.ceil(
        total_racks / 10
    ) * assumptions[
        "server_switches_per_10_racks"
    ]

    load_balancer_count = (
        total_racks
        * assumptions[
            "load_balancers_per_rack"
        ]
    )

    kvm_switch_count = (
        total_racks
        * assumptions[
            "kvm_switches_per_rack"
        ]
    )

    cable_length_ft = (
        total_racks
        * assumptions[
            "network_cable_ft_per_rack"
        ]
    )

    # ----------------------------------
    # COSTS
    # ----------------------------------

    dmz_cost = (
        dmz_switch_count
        * assumptions[
            "dmz_switch_cost"
        ]
    )

    core_cost = (
        core_switch_count
        * assumptions[
            "core_switch_cost"
        ]
    )

    server_cost = (
        server_switch_count
        * assumptions[
            "server_switch_cost"
        ]
    )

    load_balancer_cost = (
        load_balancer_count
        * assumptions[
            "load_balancer_cost"
        ]
    )

    kvm_cost = (
        kvm_switch_count
        * assumptions[
            "kvm_switch_cost"
        ]
    )

    cabling_cost = (
        cable_length_ft
        * assumptions[
            "network_cable_cost_per_ft"
        ]
    )

    total_cost = (

        dmz_cost

        + core_cost

        + server_cost

        + load_balancer_cost

        + kvm_cost

        + cabling_cost
    )

    total_cost *= (
        1 + contingency_pct
    )

    network_cost_per_rack = (
        total_cost
        / total_racks
    )

    total_network_capex_crore = (
        total_cost
        / 10000000
    )

    network_cost_per_rack_crore = (
        network_cost_per_rack
        / 10000000
    )

    return {

        "network_cost_per_rack_crore":
            network_cost_per_rack_crore,

        "total_network_capex_crore":
            total_network_capex_crore,

        "cost_breakdown": {

            "dmz_cost":
                dmz_cost,

            "core_cost":
                core_cost,

            "server_cost":
                server_cost,

            "load_balancer_cost":
                load_balancer_cost,

            "kvm_cost":
                kvm_cost,

            "cabling_cost":
                cabling_cost
        },

        "quantities": {

            "dmz_switch_count":
                dmz_switch_count,

            "core_switch_count":
                core_switch_count,

            "server_switch_count":
                server_switch_count,

            "load_balancer_count":
                load_balancer_count,

            "kvm_switch_count":
                kvm_switch_count,

            "cable_length_ft":
                cable_length_ft
        }
    }