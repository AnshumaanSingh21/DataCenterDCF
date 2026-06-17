import math
import pandas as pd


def compute_site_sizing(
    total_racks,
    kw_per_rack,
    assumptions
):

    # ----------------------------------
    # INPUTS
    # ----------------------------------

    sqft_per_rack = assumptions[
        "sqft_per_rack"
    ]

    effective_area_multiplier = assumptions[
        "effective_area_multiplier"
    ]

    rack_floors = assumptions[
        "rack_floors"
    ]

    site_coverage_pct = assumptions[
        "site_coverage_pct"
    ]

    land_cost_per_sqft_rs = assumptions[
        "land_cost_per_sqft_rs"
    ]

    # ----------------------------------
    # WHITE SPACE AREA
    # ----------------------------------

    white_space_sqft = (

        total_racks

        * sqft_per_rack
    )

    # ----------------------------------
    # GROSS BUILT-UP AREA
    # ----------------------------------

    gross_builtup_area_sqft = (

        white_space_sqft

        * effective_area_multiplier
    )

    # ----------------------------------
    # BUILDING FOOTPRINT
    # ----------------------------------

    building_footprint_sqft = (

        gross_builtup_area_sqft

        / rack_floors
    )

    # ----------------------------------
    # LAND REQUIREMENT
    # ----------------------------------

    land_area_sqft = (

        building_footprint_sqft

        / site_coverage_pct
    )

    land_area_acres = (

        land_area_sqft

        / 43560
    )

    # ----------------------------------
    # LAND COST
    # ----------------------------------

    land_cost_rs = (

        land_area_sqft

        * land_cost_per_sqft_rs
    )

    land_cost_crore = (

        land_cost_rs

        / 10000000
    )

    # ----------------------------------
    # POWER
    # ----------------------------------

    total_it_power_kw = (

        total_racks

        * kw_per_rack
    )

    total_it_power_mw = (

        total_it_power_kw

        / 1000
    )

    # ----------------------------------
    # FACILITY AREA
    # ----------------------------------

    facility_sqft = (

        gross_builtup_area_sqft
    )

    # ----------------------------------
    # SUMMARY
    # ----------------------------------

    summary_df = pd.DataFrame({

        "Metric": [

            "Total Racks",

            "White Space Area (sqft)",

            "Gross Builtup Area (sqft)",

            "Building Footprint (sqft)",

            "Land Area (sqft)",

            "Land Area (acres)",

            "Facility Area (sqft)",

            "IT Power (kW)",

            "IT Power (MW)",

            "Land Cost (Cr)"
        ],

        "Value": [

            total_racks,

            white_space_sqft,

            gross_builtup_area_sqft,

            building_footprint_sqft,

            land_area_sqft,

            land_area_acres,

            facility_sqft,

            total_it_power_kw,

            total_it_power_mw,

            land_cost_crore
        ]
    })

    # ----------------------------------
    # OUTPUT
    # ----------------------------------

    return {

        "white_space_sqft":
            white_space_sqft,

        "gross_builtup_area_sqft":
            gross_builtup_area_sqft,

        "building_footprint_sqft":
            building_footprint_sqft,

        "land_area_sqft":
            land_area_sqft,

        "land_area_acres":
            land_area_acres,

        "facility_sqft":
            facility_sqft,

        "total_it_power_kw":
            total_it_power_kw,

        "total_it_power_mw":
            total_it_power_mw,

        "land_cost_crore":
            land_cost_crore,

        "dataframes": {

            "summary_df":
                summary_df
        }
    }