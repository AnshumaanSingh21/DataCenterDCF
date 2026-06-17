import pandas as pd


def compute_it_sizing(
    total_racks,
    managed_services_penetration,
    assumptions
):

    # ----------------------------------
    # MANAGED RACKS
    # ----------------------------------

    managed_racks = int(

        total_racks

        * managed_services_penetration
    )

    # ----------------------------------
    # ASSUMPTIONS
    # ----------------------------------

    servers_per_rack = assumptions[
        "servers_per_rack"
    ]

    server_unit_cost = assumptions[
        "server_unit_cost"
    ]

    storage_units_per_system = assumptions[
        "storage_units_per_system"
    ]

    storage_unit_cost = assumptions[
        "storage_unit_cost"
    ]

    racks_per_storage_system = assumptions[
        "racks_per_storage_system"
    ]

    perimeter_firewall_cost = assumptions[
        "perimeter_firewall_cost"
    ]

    core_firewall_cost = assumptions[
        "core_firewall_cost"
    ]

    software_cost_per_rack = assumptions[
        "software_cost_per_rack"
    ]

    # ----------------------------------
    # SERVER COSTING
    # ----------------------------------

    server_cost_per_rack = (

        servers_per_rack

        * server_unit_cost
    )

    # ----------------------------------
    # STORAGE COSTING
    # ----------------------------------

    storage_cost_per_rack = (

        storage_units_per_system

        * storage_unit_cost

        / racks_per_storage_system
    )

    # ----------------------------------
    # SECURITY COSTING
    # ----------------------------------

    security_cost_per_rack = (

        perimeter_firewall_cost

        +

        core_firewall_cost
    )

    # ----------------------------------
    # TOTAL MANAGED RACK CAPEX
    # ----------------------------------

    managed_capex_per_rack = (

        server_cost_per_rack

        +

        storage_cost_per_rack

        +

        security_cost_per_rack

        +

        software_cost_per_rack
    )

    # ----------------------------------
    # TOTAL CAPEX
    # ----------------------------------

    total_managed_it_capex = (

        managed_capex_per_rack

        * managed_racks
    )

    managed_capex_per_rack_crore = (

        managed_capex_per_rack

        / 10000000
    )

    total_managed_it_capex_crore = (

        total_managed_it_capex

        / 10000000
    )

    # ----------------------------------
    # DATAFRAME
    # ----------------------------------

    summary_df = pd.DataFrame({

        "Metric": [

            "Managed Racks",

            "Server Cost per Rack",

            "Storage Cost per Rack",

            "Security Cost per Rack",

            "Software Cost per Rack",

            "Managed Capex per Rack",

            "Total Managed IT Capex"
        ],

        "Value": [

            managed_racks,

            server_cost_per_rack,

            storage_cost_per_rack,

            security_cost_per_rack,

            software_cost_per_rack,

            managed_capex_per_rack,

            total_managed_it_capex
        ]
    })

    # ----------------------------------
    # OUTPUT
    # ----------------------------------

    return {

        "managed_racks":
            managed_racks,

        "managed_capex_per_rack":
            managed_capex_per_rack,

        "managed_capex_per_rack_crore":
            managed_capex_per_rack_crore,

        "total_managed_it_capex":
            total_managed_it_capex,

        "total_managed_it_capex_crore":
            total_managed_it_capex_crore,

        "cost_breakdown": {

            "server_cost_per_rack":
                server_cost_per_rack,

            "storage_cost_per_rack":
                storage_cost_per_rack,

            "security_cost_per_rack":
                security_cost_per_rack,

            "software_cost_per_rack":
                software_cost_per_rack
        },

        "dataframes": {

            "summary_df":
                summary_df
        }
    }