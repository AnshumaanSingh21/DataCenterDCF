import os
import pandas as pd


def export_revenue_report(
    revenue_output: dict,
    file_path: str
):
    """
    Export revenue model output to Excel.
    """

    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
    )

    years = revenue_output["metadata"]["years"]

    assumptions = revenue_output[
        "assumption_register"
    ]

    # --------------------------------
    # REVENUE INPUTS SHEET
    # --------------------------------

    inputs_rows = []

    # ==================================
    # RECURRING COLOCATION REVENUE
    # ==================================

    inputs_rows.append(["RECURRING COLOCATION REVENUE"] + [""] * len(years))

    inputs_rows.append(
        ["Occupied Racks"]
        + revenue_output["drivers"]["occupied_racks"]
    )

    inputs_rows.append(
        ["Rack Revenue Per Rack"]
        + [
            assumptions["rack_mrc_crore"] * 12
            for _ in years
        ]
    )

    inputs_rows.append(
        ["YoY Escalation"]
        + [
            assumptions["rack_mrc_escalation"]
            for _ in years
        ]
    )

    inputs_rows.append(
        ["Colocation Revenue Realized"]
        + revenue_output["revenue_streams"]["recurring_colo_revenue"]
    )

    # ==================================
    # ONE TIME SETUP REVENUE
    # ==================================

    inputs_rows.append([""] + [""] * len(years))
    inputs_rows.append(["ONE TIME SETUP REVENUE"] + [""] * len(years))

    inputs_rows.append(
        ["New Racks Sold"]
        + revenue_output["drivers"]["new_racks"]
    )

    inputs_rows.append(
        ["OTC Revenue Per Rack"]
        + [
            assumptions["otc_fee_crore"]
            for _ in years
        ]
    )

    inputs_rows.append(
        ["YoY Escalation"]
        + [
            assumptions["otc_fee_escalation"]
            for _ in years
        ]
    )

    inputs_rows.append(
        ["OTC Revenue Realized"]
        + revenue_output["revenue_streams"]["otc_setup_revenue"]
    )

    # ==================================
    # RECURRING POWER REVENUE
    # ==================================

    inputs_rows.append([""] + [""] * len(years))
    inputs_rows.append(["RECURRING POWER REVENUE"] + [""] * len(years))

    inputs_rows.append(
        ["Occupied Racks"]
        + revenue_output["drivers"]["occupied_racks"]
    )

    inputs_rows.append(
        ["Power Consumed Per Rack (kW)"]
        + [
            assumptions["kw_per_rack"]
            for _ in years
        ]
    )

    inputs_rows.append(
        ["Tenant Power Tariff"]
        + [
            assumptions["utility_tariff_rs_per_kwh"]
            + assumptions["power_markup_rs_per_kwh"]
            for _ in years
        ]
    )

    inputs_rows.append(
        ["Power Revenue Per Rack"]
        + revenue_output["drivers"]["power_revenue_per_rack"]
    )

    inputs_rows.append(
        ["YoY Escalation"]
        + [
            assumptions["power_tariff_escalation"]
            for _ in years
        ]
    )

    inputs_rows.append(
        ["Power Revenue Realized"]
        + revenue_output["revenue_streams"]["power_revenue"]
    )

    # ==================================
    # SEATS REVENUE
    # ==================================

    inputs_rows.append([""] + [""] * len(years))
    inputs_rows.append(["SEATS REVENUE"] + [""] * len(years))

    inputs_rows.append(
        ["Seats Sold"]
        + [
            x * assumptions["seats_per_rack_ratio"]
            for x in revenue_output["drivers"]["occupied_racks"]
        ]
    )

    inputs_rows.append(
        ["Revenue Per Seat"]
        + [
            assumptions["seat_mrc_crore"] * 12
            for _ in years
        ]
    )

    inputs_rows.append(
        ["YoY Escalation"]
        + [
            assumptions["seat_mrc_escalation"]
            for _ in years
        ]
    )

    inputs_rows.append(
        ["Seats Revenue Realized"]
        + revenue_output["revenue_streams"]["seats_revenue"]
    )

    # ==================================
    # MANAGED SERVICES REVENUE
    # ==================================

    inputs_rows.append([""] + [""] * len(years))
    inputs_rows.append(["MANAGED SERVICES REVENUE"] + [""] * len(years))

    inputs_rows.append(
        ["Managed Racks"]
        + [
            x * assumptions["managed_services_penetration"]
            for x in revenue_output["drivers"]["occupied_racks"]
        ]
    )

    inputs_rows.append(
        ["Revenue Per Managed Rack"]
        + [
            assumptions["managed_rack_mrc_crore"] * 12
            for _ in years
        ]
    )

    inputs_rows.append(
        ["YoY Escalation"]
        + [
            assumptions["managed_rack_escalation"]
            for _ in years
        ]
    )

    inputs_rows.append(
        ["Managed Revenue Realized"]
        + revenue_output["revenue_streams"]["managed_services_revenue"]
    )

    revenue_inputs_df = pd.DataFrame(
        inputs_rows,
        columns=["Line Item"] + years
    )

    # --------------------------------
    # REVENUE PROJECTION
    # --------------------------------

    revenue_df = pd.DataFrame({

        "Year":
            years,

        "Recurring Colo Revenue":
            revenue_output["revenue_streams"]["recurring_colo_revenue"],

        "OTC Setup Revenue":
            revenue_output["revenue_streams"]["otc_setup_revenue"],

        "Power Revenue":
            revenue_output["revenue_streams"]["power_revenue"],

        "Seats Revenue":
            revenue_output["revenue_streams"]["seats_revenue"],

        "Managed Services Revenue":
            revenue_output["revenue_streams"]["managed_services_revenue"],

        "Cross Connect Revenue":
            revenue_output["revenue_streams"]["cross_connect_revenue"],

        "Remote Hands Revenue":
            revenue_output["revenue_streams"]["remote_hands_revenue"],

        "Professional Services Revenue":
            revenue_output["revenue_streams"]["professional_services_revenue"],

        "DR Services Revenue":
            revenue_output["revenue_streams"]["dr_services_revenue"],

        "Gross Revenue":
            revenue_output["revenue_streams"]["gross_revenue"],

        "Net Revenue":
            revenue_output["revenue_streams"]["net_revenue"]
    })

    # --------------------------------
    # DRIVERS
    # --------------------------------

    drivers_df = pd.DataFrame({

        "Year":
            years,

        "Occupied Racks":
            revenue_output["drivers"]["occupied_racks"],

        "New Racks":
            revenue_output["drivers"]["new_racks"],

        "IT Load (kW)":
            revenue_output["drivers"]["it_load_kw"],

        "Facility Load (kW)":
            revenue_output["drivers"]["facility_load_kw"],

        "Power Revenue Per Rack":
            revenue_output["drivers"]["power_revenue_per_rack"]
    })

    # --------------------------------
    # ASSUMPTIONS
    # --------------------------------

    assumptions_df = pd.DataFrame(
        list(
            assumptions.items()
        ),
        columns=[
            "Assumption",
            "Value"
        ]
    )

    # --------------------------------
    # EXPORT
    # --------------------------------

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl"
    ) as writer:

        revenue_inputs_df.to_excel(
            writer,
            sheet_name="Revenue Inputs",
            index=False
        )

        revenue_df.to_excel(
            writer,
            sheet_name="Revenue Projection",
            index=False
        )

        drivers_df.to_excel(
            writer,
            sheet_name="Drivers",
            index=False
        )

        assumptions_df.to_excel(
            writer,
            sheet_name="Assumptions",
            index=False
        )

    print(
        f"\nRevenue report exported to:\n{file_path}"
    )