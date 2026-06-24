import math
import pandas as pd


def escalate(base, rate, years):

    return [
        base * ((1 + rate) ** i)
        for i in range(years)
    ]


def compute_opex(
    revenue_output,
    capex_output,
    assumptions
):

    years = len(
        revenue_output["metadata"]["years"]
    )

    year_labels = (
        revenue_output["metadata"]["years"]
    )

    occupied_racks = (
        revenue_output["drivers"]
        ["occupied_racks"]
    )

    net_revenue = (
        revenue_output["revenue_streams"]
        ["net_revenue"]
    )

    power_cost = (
        revenue_output["power_detail"]
        ["power_cost"]
    )

    facility_sqft = (

        capex_output[
            "site_sizing"
        ][
            "facility_sqft"
        ]
    )

    # -----------------------------
    # MANPOWER
    # -----------------------------

    fte_count = [

        math.ceil(
            racks
            / 100
            * assumptions[
                "fte_per_100_racks"
            ]
        )

        for racks in occupied_racks
    ]

    employee_cost_crore = escalate(

        assumptions[
            "avg_ctc_per_employee_lakh"
        ] / 100,

        assumptions[
            "manpower_escalation"
        ],

        years
    )

    manpower_cost = [

        fte_count[i]
        * employee_cost_crore[i]

        for i in range(years)
    ]

    # -----------------------------
    # HOUSEKEEPING
    # -----------------------------

    construction_years = assumptions.get("construction_years", 0)

    housekeeping_cost = [

        0.0 if i < construction_years else (

            facility_sqft

            * assumptions[
                "housekeeping_rate_per_sqft"
            ]

            * (

                (1 + assumptions[
                    "housekeeping_escalation"
                ]) ** i

            )

            / 10000000

        )

        for i in range(years)
    ]

    # -----------------------------
    # MAINTENANCE (ASSET BASED)
    # -----------------------------

    civil_capex = (
        capex_output[
            "capex_components"
        ][
            "civil_capex"
        ]
    )

    electrical_capex = (
        capex_output[
            "capex_components"
        ][
            "electrical_capex"
        ]
    )

    mechanical_capex = (
        capex_output[
            "capex_components"
        ][
            "mechanical_capex"
        ]
    )

    network_capex_base = (
        capex_output[
            "capex_components"
        ][
            "network_capex"
        ]
    )

    software_capex = (
        capex_output[
            "capex_components"
        ][
            "software_capex"
        ]
    )

    cumulative_civil = []
    cumulative_electrical = []
    cumulative_mechanical = []
    cumulative_network = []
    cumulative_software = []

    running_civil = 0
    running_electrical = 0
    running_mechanical = 0
    running_network = 0
    running_software = 0

    for i in range(years):

        running_civil += civil_capex[i]

        running_electrical += electrical_capex[i]

        running_mechanical += mechanical_capex[i]

        running_network += network_capex_base[i]

        running_software += software_capex[i]

        cumulative_civil.append(
            running_civil
        )

        cumulative_electrical.append(
            running_electrical
        )

        cumulative_mechanical.append(
            running_mechanical
        )

        cumulative_network.append(
            running_network
        )

        cumulative_software.append(
            running_software
        )

    maintenance_cost = []

    for i in range(years):

        if i < construction_years:
            maintenance_cost.append(0.0)
            continue

        maintenance_cost.append(

            cumulative_civil[i]
            * assumptions[
                "civil_amc_pct"
            ]

            +

            cumulative_electrical[i]
            * assumptions[
                "electrical_amc_pct"
            ]

            +

            cumulative_mechanical[i]
            * assumptions[
                "mechanical_amc_pct"
            ]

            +

            cumulative_network[i]
            * assumptions[
                "network_amc_pct"
            ]

            +

            cumulative_software[i]
            * assumptions[
                "software_amc_pct"
            ]
        )
      

    

    # -----------------------------
    # NETWORK
    # -----------------------------

    network_cost = [

        revenue
        * assumptions[
            "network_pct_of_revenue"
        ]

        for revenue in net_revenue
    ]

    # -----------------------------
    # SECURITY
    # -----------------------------

    security_cost = [

        revenue
        * assumptions[
            "security_pct_of_revenue"
        ]

        for revenue in net_revenue
    ]

    # -----------------------------
    # INSURANCE
    # -----------------------------

    asset_value = (
        capex_output[
            "financials"
        ][
            "cumulative_capex"
        ]
    )

    insurance_cost = [

        asset_value[i]

        * assumptions[
            "insurance_pct_of_asset_value"
        ]

        for i in range(years)
    ]

    # -----------------------------
    # PROPERTY TAX
    # Levied on full asset base
    # (land + building + equipment),
    # not land alone.
    # -----------------------------

    property_tax = [

        asset_value[i]

        * assumptions[
            "property_tax_pct_of_asset_value"
        ]

        for i in range(years)
    ]

    

    # -----------------------------
    # MARKETING
    # -----------------------------

    mkt_start = assumptions.get("marketing_pct_start", 0.01)
    mkt_end   = assumptions.get("marketing_pct_end",   0.0025)
    marketing_cost = [
        net_revenue[i] * max(mkt_end, mkt_start - (mkt_start - mkt_end) * i / max(years - 1, 1))
        for i in range(years)
    ]

    # -----------------------------
    # G&A
    # -----------------------------

    gna_cost = [

        revenue
        * assumptions[
            "gna_pct_of_revenue"
        ]

        for revenue in net_revenue
    ]

    # -----------------------------
    # TOTAL OPEX
    # -----------------------------

    total_opex = []

    for i in range(years):

        total_opex.append(

            power_cost[i]

            + manpower_cost[i]

            + housekeeping_cost[i]

            + maintenance_cost[i]

            + network_cost[i]

            + security_cost[i]

            + insurance_cost[i]

            + property_tax[i]

            + marketing_cost[i]

            + gna_cost[i]
        )

    # -----------------------------
    # EBITDA
    # -----------------------------

    ebitda = [

        net_revenue[i]
        - total_opex[i]

        for i in range(years)
    ]

    ebitda_margin = [

        (
            ebitda[i]
            / net_revenue[i]
        )

        if net_revenue[i] > 0
        else 0

        for i in range(years)
    ]

    # -----------------------------
    # DATAFRAMES
    # -----------------------------

    drivers_df = pd.DataFrame({

        "Year":
            year_labels,

        "FTE Count":
            fte_count
    })

    cost_lines_df = pd.DataFrame({

        "Year":
            year_labels,

        "Power Cost":
            power_cost,

        "Manpower Cost":
            manpower_cost,

        "Housekeeping Cost":
            housekeeping_cost,

        "Maintenance Cost":
            maintenance_cost,

        "Network Cost":
            network_cost,

        "Security Cost":
            security_cost,

        "Insurance Cost":
            insurance_cost,

        "Property Tax":
            property_tax,

        "Marketing Cost":
            marketing_cost,

        "G&A Cost":
            gna_cost,

        "Total Opex":
            total_opex
    })

    financials_df = pd.DataFrame({

        "Year":
            year_labels,

        "Net Revenue":
            net_revenue,

        "EBITDA":
            ebitda,

        "EBITDA Margin":
            ebitda_margin
    })

    # -----------------------------
    # OUTPUT
    # -----------------------------

    return {

        "metadata": {

            "years":
                year_labels
        },

        "drivers": {

            "fte_count":
                fte_count,

            "facility_sqft":
                facility_sqft
        },

        "cost_lines": {

            "power_cost":
                power_cost,

            "manpower_cost":
                manpower_cost,

            "housekeeping_cost":
                housekeeping_cost,

            "maintenance_cost":
                maintenance_cost,

            "network_cost":
                network_cost,

            "security_cost":
                security_cost,

            "insurance_cost":
                insurance_cost,

            "property_tax":
                property_tax,

            "marketing_cost":
                marketing_cost,

            "gna_cost":
                gna_cost
        },

        "financials": {

            "net_revenue":
                net_revenue,

            "total_opex":
                total_opex,

            "ebitda":
                ebitda,

            "ebitda_margin":
                ebitda_margin
        },

        "dataframes": {

            "drivers_df":
                drivers_df,

            "cost_lines_df":
                cost_lines_df,

            "financials_df":
                financials_df
        },

        "assumption_register":
            assumptions.copy()
    }