import pandas as pd

from src.engines.site_sizing_engine import (
    compute_site_sizing
)

from src.engines.it_sizing_engine import (
    compute_it_sizing
)

from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from src.engines.network_sizing_engine import (
    compute_network_sizing
)

from assumptions.revenue_defaults import (
    get_default_revenue_assumptions,
    FACILITY_TYPE_OVERRIDES
)

from src.engines.capex_sizing_engine import (
    compute_electrical_sizing
)


def compute_capex(
    user_inputs,
    assumptions
):

    years = user_inputs["projection_years"]
    start_year = user_inputs.get("start_year", 2026)

    year_labels = list(
        range(
            start_year,
            start_year + years
        )
    )

    # ----------------------------------
    # FACILITY CHARACTERISTICS
    # ----------------------------------

    revenue_assumptions = (
        get_default_revenue_assumptions()
    )

    facility_type = user_inputs.get(
        "facility_type",
        "wholesale"
    )

    if facility_type in FACILITY_TYPE_OVERRIDES:

        revenue_assumptions.update(

            FACILITY_TYPE_OVERRIDES[
                facility_type
            ]
        )

    kw_per_rack = (
        revenue_assumptions[
            "kw_per_rack"
        ]
    )

    pue = (
        revenue_assumptions[
            "pue"
        ]
    )

    # ----------------------------------
    # SITE SIZING
    # ----------------------------------

    site_sizing = (

        compute_site_sizing(

            total_racks=
                user_inputs[
                    "total_racks"
                ],

            kw_per_rack=
                kw_per_rack,

            assumptions=
                assumptions
        )
    )

    # ----------------------------------
    # ELECTRICAL SIZING
    # ----------------------------------

    electrical_sizing = (

        compute_electrical_sizing(

            total_racks=
                user_inputs[
                    "total_racks"
                ],

            kw_per_rack=
                kw_per_rack,

            pue=
                pue,

            assumptions=
                assumptions
        )
    )

    electrical_cost_per_rack = (

        electrical_sizing[
            "electrical_capex_per_rack_crore"
        ]
    )

    # ----------------------------------
    # DEPLOYMENT SCHEDULE
    # ----------------------------------

    racks_deployed = [0] * years

    phase_years = [

        assumptions["phase_1_year"],
        assumptions["phase_2_year"],
        assumptions["phase_3_year"]
    ]

    phase_racks = [

        assumptions["phase_1_racks"],
        assumptions["phase_2_racks"],
        assumptions["phase_3_racks"]
    ]

    for phase_idx in range(3):

        deployment_year = (
            phase_years[phase_idx]
        )

        if deployment_year < years:

            racks_deployed[
                deployment_year
            ] = phase_racks[
                phase_idx
            ]

    # ----------------------------------
    # CAPEX COMPONENTS
    # ----------------------------------

    civil_capex = [

        racks

        * assumptions[
            "civil_cost_per_rack"
        ]

        for racks in racks_deployed
    ]

    electrical_capex = [

        racks

        * electrical_cost_per_rack

        for racks in racks_deployed
    ]

    mechanical_capex = [

        racks

        * assumptions[
            "mechanical_cost_per_rack"
        ]

        for racks in racks_deployed
    ]

    network_sizing = compute_network_sizing(

        total_racks=user_inputs["total_racks"],

        assumptions=assumptions
    )

    network_cost_per_rack = (

        network_sizing[
            "network_cost_per_rack_crore"
        ]
    )

    network_capex = [

        racks
        * network_cost_per_rack

        for racks in racks_deployed
    ]

    # ----------------------------------
    # IT SIZING
    # ----------------------------------

    revenue_assumptions = (
        get_default_revenue_assumptions()
    )

    it_sizing = compute_it_sizing(

        total_racks=user_inputs[
            "total_racks"
        ],

        managed_services_penetration=
            revenue_assumptions[
                "managed_services_penetration"
            ],

        assumptions=assumptions
    )

    managed_capex_per_rack = (

        it_sizing[
            "managed_capex_per_rack_crore"
        ]
    )

    managed_services_penetration = (

        revenue_assumptions[
            "managed_services_penetration"
        ]
    )

    effective_it_capex_per_rack = (

        assumptions[
            "it_hardware_cost_per_rack"
        ]

        +

        managed_services_penetration

        *

        managed_capex_per_rack
    )

    it_hardware_capex = [

        racks

        * effective_it_capex_per_rack

        for racks in racks_deployed
    ]



   
    # ----------------------------------
    # SITE LEVEL COSTS
    # ----------------------------------

    software_capex = [0] * years

    software_capex[0] = (

        assumptions[
            "dcim_cost_crore"
        ]

        +

        assumptions[
            "virtualization_cost_crore"
        ]
    )

    site_level_capex = [0] * years

    site_level_capex[0] = (

        site_sizing[
            "land_cost_crore"
        ]

        +

        assumptions[
            "consultancy_cost_crore"
        ]

        +

        assumptions[
            "approval_cost_crore"
        ]

        +

        assumptions.get(
            "misc_infrastructure_cost_crore",
            0
        )
    )
    # ----------------------------------
    # PRE OP
    # ----------------------------------

    pre_op_capex = []

    for i in range(years):

        deployment_capex = (

            civil_capex[i]

            +

            electrical_capex[i]

            +

            mechanical_capex[i]

            +

            network_capex[i]

            +

            it_hardware_capex[i]

        )

        pre_op_capex.append(

            deployment_capex

            *

            assumptions[
                "pre_op_pct"
            ]
        )
    # ----------------------------------
    # TOTAL CAPEX
    # ----------------------------------

    total_capex = []

    for i in range(years):

        total_capex.append(

            civil_capex[i]

            +

            electrical_capex[i]

            +

            mechanical_capex[i]

            +

            network_capex[i]

            +

            it_hardware_capex[i]


            +

            software_capex[i]

            +

            site_level_capex[i]

            +

            pre_op_capex[i]
        )

    cumulative_capex = []

    running_total = 0

    for value in total_capex:

        running_total += value

        cumulative_capex.append(
            running_total
        )

    # ----------------------------------
    # DATAFRAME
    # ----------------------------------

    capex_df = pd.DataFrame({

        "Year":
            year_labels,

        "Racks Deployed":
            racks_deployed,

        "Civil":
            civil_capex,

        "Electrical":
            electrical_capex,

        "Mechanical":
            mechanical_capex,

        "Network":
            network_capex,

        "IT Hardware":
            it_hardware_capex,

        
        "Software":
            software_capex,

        "Site Level (Land+Consult)":
            site_level_capex,

        "Pre Op":
            pre_op_capex,

        "Total Capex":
            total_capex,

        "Cumulative Capex":
            cumulative_capex
    })

    # ----------------------------------
    # OUTPUT
    # ----------------------------------

    return {

        "metadata": {

            "years":
                year_labels
        },

        "drivers": {

            "racks_deployed":
                racks_deployed,

            "electrical_capex_per_rack":
                electrical_cost_per_rack,

            "kw_per_rack":
                kw_per_rack,

            "pue":
                pue
        },

        "deployment_schedule": [

            {
                "year":
                    phase_years[i],

                "racks":
                    phase_racks[i]
            }

            for i in range(
                len(phase_years)
            )

            if phase_racks[i] > 0
        ],

        "electrical_sizing":
            electrical_sizing,

        "network_sizing":
            network_sizing,

        "it_sizing":
            it_sizing,

        "site_sizing":
            site_sizing,

        "capex_components": {

            "civil_capex":
                civil_capex,

            "electrical_capex":
                electrical_capex,

            "mechanical_capex":
                mechanical_capex,

            "network_capex":
                network_capex,

            "it_hardware_capex":
                it_hardware_capex,

            "software_capex":
                software_capex,

            "site_level_capex":
                site_level_capex,

            "pre_op_capex":
                pre_op_capex
        },

        "financials": {

            "total_capex":
                total_capex,

            "cumulative_capex":
                cumulative_capex
        },

        "dataframes": {

            "capex_df":
                capex_df
        },

        "assumption_register":
            assumptions.copy()
    }
