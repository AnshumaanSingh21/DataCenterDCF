import pandas as pd


def compute_depreciation(
    capex_output,
    assumptions
):

    years = len(
        capex_output["metadata"]["years"]
    )

    civil_capex = (
        capex_output["capex_components"]
        ["civil_capex"]
    )

    electrical_capex = (
        capex_output["capex_components"]
        ["electrical_capex"]
    )

    mechanical_capex = (
        capex_output["capex_components"]
        ["mechanical_capex"]
    )

    network_capex = (
        capex_output["capex_components"]
        ["network_capex"]
    )

    software_capex = (
        capex_output["capex_components"]
        ["software_capex"]
    )

    it_hardware_capex = (
        capex_output["capex_components"]
        ["it_hardware_capex"]
    )

    civil_dep = [0] * years
    electrical_dep = [0] * years
    mechanical_dep = [0] * years
    network_dep = [0] * years
    software_dep = [0] * years
    it_dep = [0] * years

    # --------------------------------
    # STRAIGHT LINE DEPRECIATION
    # --------------------------------

    for purchase_year in range(years):

        for future_year in range(
            purchase_year,
            years
        ):

            civil_dep[future_year] += (
                civil_capex[purchase_year]
                /
                assumptions["civil_life_years"]
            )

            electrical_dep[future_year] += (
                electrical_capex[purchase_year]
                /
                assumptions["electrical_life_years"]
            )

            mechanical_dep[future_year] += (
                mechanical_capex[purchase_year]
                /
                assumptions["mechanical_life_years"]
            )

            network_dep[future_year] += (
                network_capex[purchase_year]
                /
                assumptions["network_life_years"]
            )

            software_dep[future_year] += (
                software_capex[purchase_year]
                /
                assumptions["software_life_years"]
            )

            it_dep[future_year] += (
                it_hardware_capex[purchase_year]
                /
                assumptions["it_hardware_life_years"]
            )

    total_depreciation = []

    for i in range(years):

        total_depreciation.append(

            civil_dep[i]

            + electrical_dep[i]

            + mechanical_dep[i]

            + network_dep[i]

            + software_dep[i]

            + it_dep[i]
        )

    accumulated_depreciation = []

    running_total = 0

    for dep in total_depreciation:

        running_total += dep

        accumulated_depreciation.append(
            running_total
        )

    total_capex = (
        capex_output["financials"]
        ["cumulative_capex"]
    )

    net_book_value = []

    for i in range(years):

        net_book_value.append(

            total_capex[i]

            -

            accumulated_depreciation[i]
        )

    depreciation_df = pd.DataFrame({

        "Year":
            capex_output["metadata"]["years"],

        "Civil Depreciation":
            civil_dep,

        "Electrical Depreciation":
            electrical_dep,

        "Mechanical Depreciation":
            mechanical_dep,

        "Network Depreciation":
            network_dep,

        "Software Amortization":
            software_dep,

        "IT Depreciation":
            it_dep,

        "Total Depreciation":
            total_depreciation,

        "Accumulated Depreciation":
            accumulated_depreciation,

        "Net Book Value":
            net_book_value
    })

    return {

        "financials": {

            "total_depreciation":
                total_depreciation,

            "accumulated_depreciation":
                accumulated_depreciation,

            "net_book_value":
                net_book_value
        },

        "dataframes": {

            "depreciation_df":
                depreciation_df
        },

        "assumption_register":
            assumptions.copy()
    }