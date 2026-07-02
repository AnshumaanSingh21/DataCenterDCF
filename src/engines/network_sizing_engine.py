import math


def compute_network_sizing(total_racks, assumptions):

    contingency_pct = assumptions["network_contingency_pct"]

    # ----------------------------------
    # QUANTITIES
    # ----------------------------------

    # Fixed-count equipment: same count regardless of phase rack count.
    # Perimeter and spine switches are facility-level, not rack-scaled.
    perimeter_switch_count = assumptions["perimeter_switch_count"]
    spine_switch_count     = assumptions["spine_switch_count"]

    # Per-zone equipment: scales with rack count.
    server_switch_count = (
        math.ceil(total_racks / 10)
        * assumptions["server_switches_per_10_racks"]
    )

    # Load balancers = 0 in colo (tenant-provided). Kept as a parameter
    # so wholesale/managed models can activate it.
    load_balancer_count = (
        total_racks * assumptions["load_balancers_per_rack"]
    )

    # 1 IP KVM per rack for out-of-band hardware management.
    kvm_switch_count = (
        total_racks * assumptions["kvm_switches_per_rack"]
    )

    cable_length_ft = (
        total_racks * assumptions["network_cable_ft_per_rack"]
    )

    # ----------------------------------
    # COSTS
    # ----------------------------------

    perimeter_cost     = perimeter_switch_count * assumptions["perimeter_switch_cost"]
    spine_cost         = spine_switch_count     * assumptions["spine_switch_cost"]
    server_cost        = server_switch_count    * assumptions["server_switch_cost"]
    load_balancer_cost = load_balancer_count    * assumptions["load_balancer_cost"]
    kvm_cost           = kvm_switch_count       * assumptions["kvm_switch_cost"]
    cabling_cost       = cable_length_ft        * assumptions["network_cable_cost_per_ft"]

    # Meet-me room / interconnection fit-out: the infrastructure that enables
    # cross-connect revenue (patch frames, backbone fibre, carrier entry).
    meet_me_room_cost  = total_racks * assumptions.get("meet_me_room_cost_per_rack", 0)

    total_cost = (
        perimeter_cost
        + spine_cost
        + server_cost
        + load_balancer_cost
        + kvm_cost
        + cabling_cost
        + meet_me_room_cost
    )

    total_cost *= (1 + contingency_pct)

    network_cost_per_rack       = total_cost / total_racks
    total_network_capex_crore   = total_cost / 10_000_000
    network_cost_per_rack_crore = network_cost_per_rack / 10_000_000

    return {

        "network_cost_per_rack_crore":  network_cost_per_rack_crore,
        "total_network_capex_crore":    total_network_capex_crore,

        "cost_breakdown": {
            "perimeter_cost":    perimeter_cost,
            "spine_cost":        spine_cost,
            "server_cost":       server_cost,
            "load_balancer_cost": load_balancer_cost,
            "kvm_cost":          kvm_cost,
            "cabling_cost":      cabling_cost,
            "meet_me_room_cost": meet_me_room_cost,
        },

        "quantities": {
            "perimeter_switch_count": perimeter_switch_count,
            "spine_switch_count":     spine_switch_count,
            "server_switch_count":    server_switch_count,
            "load_balancer_count":    load_balancer_count,
            "kvm_switch_count":       kvm_switch_count,
            "cable_length_ft":        cable_length_ft,
        },
    }
