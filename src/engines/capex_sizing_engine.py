import math


def compute_electrical_sizing(
    total_racks,
    kw_per_rack,
    pue,
    assumptions
):

    # =====================================================
    # LOAD CALCULATIONS
    # =====================================================

    it_load_kw = (

        total_racks
        * kw_per_rack
    )

    facility_load_kw = (

        it_load_kw
        * pue
    )

    misc_infra_load_kw = (

        facility_load_kw
        - it_load_kw
    )

    contingency = (
        assumptions["contingency_pct"]
    )

    # =====================================================
    # UPS SIZING
    # =====================================================

    ups_active_kw = (

        assumptions["ups_active_modules"]

        *

        assumptions["ups_module_kva"]

        *

        assumptions["ups_power_factor"]
    )

    ups_frames_required = math.ceil(

        facility_load_kw
        / ups_active_kw
    )

    total_ups_frames = (

        ups_frames_required
        * 2
    )  # N+N

    ups_cost_per_frame = (

        assumptions["ups_active_modules"]

        *

        assumptions["ups_module_cost"]

        +

        assumptions["ups_frame_cost"]
    )

    ups_total_cost = (

        total_ups_frames
        * ups_cost_per_frame
        * (1 + contingency)
    )

    # =====================================================
    # BATTERY SIZING
    # =====================================================

    required_battery_kwh = (

        facility_load_kw

        *

        assumptions[
            "battery_backup_hours"
        ]
    )

    battery_count = math.ceil(

        required_battery_kwh

        /

        assumptions[
            "battery_unit_kwh"
        ]
    )

    battery_total_cost = (

        battery_count

        *

        assumptions[
            "battery_unit_cost"
        ]

        *

        (1 + contingency)
    )

    # =====================================================
    # DG SIZING
    # =====================================================

    dg_net_kw = (

        assumptions[
            "dg_rated_kva"
        ]

        *

        assumptions[
            "dg_power_factor"
        ]

        *

        assumptions[
            "dg_load_factor"
        ]
    )

    total_dgs = (

        math.ceil(
            facility_load_kw
            / dg_net_kw
        )

        + 1
    )  # N+1

    dg_cost_per_unit = (

        assumptions[
            "dg_supply_cost"
        ]

        +

        assumptions[
            "dg_acm_cost"
        ]

        +

        assumptions[
            "dg_installation_cost"
        ]
    )

    dg_total_cost = (

        total_dgs

        *

        dg_cost_per_unit

        *

        (1 + contingency)
    )

    # =====================================================
    # TRANSFORMER SIZING
    # =====================================================

    transformer_net_kw = (

        assumptions[
            "transformer_kva"
        ]

        *

        assumptions[
            "transformer_power_factor"
        ]

        *

        assumptions[
            "transformer_load_factor"
        ]
    )

    total_transformers = (

        math.ceil(
            facility_load_kw
            / transformer_net_kw
        )

        + 1
    )  # N+1

    transformer_cost_per_unit = (

        assumptions[
            "transformer_supply_cost"
        ]

        +

        assumptions[
            "transformer_panel_cost"
        ]
    )

    transformer_total_cost = (

        total_transformers

        *

        transformer_cost_per_unit

        *

        (1 + contingency)
    )

    # =====================================================
    # PDU / DISTRIBUTION
    # =====================================================

    pdu_cost_per_rack = (

        assumptions[
            "pdus_per_rack"
        ]

        *

        assumptions[
            "pdu_panel_cost"
        ]

        +

        (
            assumptions[
                "ups_db_per_20_racks"
            ]
            / 20
        )

        *

        assumptions[
            "ups_db_cost"
        ]

        +

        assumptions[
            "lighting_per_rack"
        ]

        *

        assumptions[
            "lighting_cost"
        ]

        +

        assumptions[
            "earthing_per_rack"
        ]

        *

        assumptions[
            "earthing_cost"
        ]
    )

    pdu_total_cost = (

        pdu_cost_per_rack

        *

        total_racks

        *

        (1 + contingency)
    )

    # =====================================================
    # CABLING
    # =====================================================

    cabling_cost_per_rack = (

        assumptions[
            "cable_length_per_rack"
        ]

        *

        assumptions[
            "wiring_cost_per_ft"
        ]

        +

        assumptions[
            "cable_tray_per_rack"
        ]

        *

        assumptions[
            "cable_tray_cost_per_ft"
        ]

        +

        assumptions[
            "ats_per_rack"
        ]

        *

        assumptions[
            "ats_cost"
        ]
    )

    cabling_total_cost = (

        cabling_cost_per_rack

        *

        total_racks

        *

        (1 + contingency)
    )

    # =====================================================
    # TOTAL ELECTRICAL CAPEX
    # =====================================================

    electrical_total_cost = (

        ups_total_cost

        +

        battery_total_cost

        +

        dg_total_cost

        +

        transformer_total_cost

        +

        pdu_total_cost

        +

        cabling_total_cost
    )

    electrical_cost_per_rack = (

        electrical_total_cost
        / total_racks
    )

    # convert INR → Crore

    electrical_total_cost_crore = (

        electrical_total_cost
        / 10000000
    )

    electrical_cost_per_rack_crore = (

        electrical_cost_per_rack
        / 10000000
    )

    # =====================================================
    # OUTPUT
    # =====================================================

    return {

        "loads": {

            "it_load_kw":
                it_load_kw,

            "facility_load_kw":
                facility_load_kw,

            "misc_infra_load_kw":
                misc_infra_load_kw
        },

        "equipment_counts": {

            "ups_frames":
                total_ups_frames,

            "battery_count":
                battery_count,

            "dg_count":
                total_dgs,

            "transformer_count":
                total_transformers
        },

        "capex_breakdown": {

            "ups_capex_crore":
                ups_total_cost / 10000000,

            "battery_capex_crore":
                battery_total_cost / 10000000,

            "dg_capex_crore":
                dg_total_cost / 10000000,

            "transformer_capex_crore":
                transformer_total_cost / 10000000,

            "pdu_capex_crore":
                pdu_total_cost / 10000000,

            "cabling_capex_crore":
                cabling_total_cost / 10000000
        },

        "electrical_capex_total_crore":
            electrical_total_cost_crore,

        "electrical_capex_per_rack_crore":
            electrical_cost_per_rack_crore
    }