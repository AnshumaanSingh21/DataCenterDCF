import pandas as pd

from assumptions.revenue_defaults import (
    get_default_revenue_assumptions,
    FACILITY_TYPE_OVERRIDES,
)


def escalate(base, rate, years):
    return [
        base * ((1 + rate) ** i)
        for i in range(years)
    ]


def compute_revenue(user_inputs, assumptions):

    facility_type = user_inputs["facility_type"]

    # ---------------------------------
    # APPLY FACILITY OVERRIDES
    # ---------------------------------

    overrides = FACILITY_TYPE_OVERRIDES.get(
        facility_type,
        {}
    )

    assumptions.update(overrides)

    years = user_inputs["projection_years"]
    total_racks = user_inputs["total_racks"]

    lease_up = assumptions["lease_up_curve"][:years]

    # ---------------------------------
    # LEASE UP
    # ---------------------------------

    occupied_racks = [
        total_racks * x
        for x in lease_up
    ]

    new_racks = []

    for i in range(len(occupied_racks)):

        if i == 0:
            new_racks.append(
                occupied_racks[i]
            )

        else:
            new_racks.append(
                max(
                    occupied_racks[i]
                    - occupied_racks[i - 1],
                    0
                )
            )

    # ---------------------------------
    # PHYSICAL LAYER
    # ---------------------------------

    kw_per_rack = assumptions["kw_per_rack"]

    pue = assumptions["pue"]

    it_load_kw = [
        x * kw_per_rack
        for x in occupied_racks
    ]

    facility_load_kw = [
        x * pue
        for x in it_load_kw
    ]

    # ---------------------------------
    # ESCALATIONS
    # ---------------------------------

    rack_mrc = escalate(
        assumptions["rack_mrc_crore"],
        assumptions["rack_mrc_escalation"],
        years
    )

    otc_fee = escalate(
        assumptions["otc_fee_crore"],
        assumptions["otc_fee_escalation"],
        years
    )

    utility_tariff = escalate(
        assumptions["utility_tariff_rs_per_kwh"],
        assumptions["power_tariff_escalation"],
        years
    )

    customer_tariff = escalate(
        assumptions["utility_tariff_rs_per_kwh"]
        + assumptions["power_markup_rs_per_kwh"],
        assumptions["power_tariff_escalation"],
        years
    )

    seat_mrc = escalate(
        assumptions["seat_mrc_crore"],
        assumptions["seat_mrc_escalation"],
        years
    )

    managed_mrc = escalate(
        assumptions["managed_rack_mrc_crore"],
        assumptions["managed_rack_escalation"],
        years
    )

    # ---------------------------------
    # RACK REVENUE
    # ---------------------------------

    rack_revenue = [
        occupied_racks[i]
        * rack_mrc[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # OTC REVENUE
    # ---------------------------------

    otc_revenue = [
        new_racks[i]
        * otc_fee[i]
        for i in range(years)
    ]

    # ---------------------------------
    # POWER REVENUE
    # ---------------------------------

    divisor = assumptions["crore_divisor"]

    hours_per_year = 24 * 365

    power_units_per_rack = [
        kw_per_rack * hours_per_year
        for _ in range(years)
    ]

    power_revenue_per_rack = [

        (
            kw_per_rack
            * pue
            * hours_per_year
            * customer_tariff[i]
        )
 
        for i in range(years)
    ]

    power_revenue = [

        (
            occupied_racks[i]
            * power_revenue_per_rack[i]
        ) / divisor

        for i in range(years)
    ]

    power_cost = [

        (
            facility_load_kw[i]
            * utility_tariff[i]
            * hours_per_year
        ) / divisor

        for i in range(years)
    ]

    power_margin = [

        power_revenue[i]
        - power_cost[i]

        for i in range(years)
    ]

    # ---------------------------------
    # SEATS REVENUE
    # ---------------------------------

    seats_sold = [
        occupied_racks[i]
        * assumptions["seats_per_rack_ratio"]
        for i in range(years)
    ]

    seats_revenue = [
        seats_sold[i]
        * seat_mrc[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # MANAGED REVENUE
    # ---------------------------------

    penetration = (
        assumptions["managed_services_penetration"]
        if facility_type == "retail_colo"
        else 0.0
    )

    managed_racks = [
        occupied_racks[i]
        * penetration
        for i in range(years)
    ]

    managed_revenue = [
        managed_racks[i]
        * managed_mrc[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # TOTAL REVENUE
    # ---------------------------------

    total_revenue = []

    for i in range(years):

        total_revenue.append(
            rack_revenue[i]
            + otc_revenue[i]
            + power_revenue[i]
            + seats_revenue[i]
            + managed_revenue[i]
        )

    dot_deduction = [
        x * assumptions["dot_share_pct"]
        for x in total_revenue
    ]

    net_revenue = [
        total_revenue[i]
        - dot_deduction[i]
        for i in range(years)
    ]

    # ---------------------------------
    # VALIDATIONS
    # ---------------------------------

    assert all(
        x <= total_racks
        for x in occupied_racks
    ), "Occupied racks exceed capacity"

    assert all(
        x >= 0
        for x in new_racks
    ), "Negative new racks"

    # ---------------------------------
    # OUTPUT
    # ---------------------------------

    return {

        "metadata": {

            "location": user_inputs["location"],

            "facility_type": facility_type,

            "projection_years": years,

            "total_racks": total_racks,

            "years": list(
                range(
                    2026,
                    2026 + years
                )
            )
        },

        "drivers": {

            "occupied_racks": occupied_racks,

            "new_racks": new_racks,

            "it_load_kw": it_load_kw,

            "facility_load_kw": facility_load_kw,

            "rack_mrc": rack_mrc,

            "otc_fee": otc_fee,

            "customer_tariff": customer_tariff,

            "seat_mrc": seat_mrc,

            "managed_mrc": managed_mrc,

            "power_revenue_per_rack":
                power_revenue_per_rack
        },

        "revenue_streams": {

            "rack_revenue": rack_revenue,

            "otc_revenue": otc_revenue,

            "power_revenue": power_revenue,

            "seats_revenue": seats_revenue,

            "managed_revenue": managed_revenue
        },

        "financials": {

            "power_cost": power_cost,

            "power_margin": power_margin,

            "total_revenue": total_revenue,

            "dot_deduction": dot_deduction,

            "net_revenue": net_revenue
        },

        "assumption_register": assumptions.copy()
    }


if __name__ == "__main__":

    user_inputs = {
        "location": "Mumbai",
        "total_racks": 1000,
        "facility_type": "retail_colo",
        "projection_years": 10,
    }

    assumptions = (
        get_default_revenue_assumptions()
    )

    output = compute_revenue(
        user_inputs,
        assumptions
    )

    revenue_df = pd.DataFrame({

        "Year":
            output["metadata"]["years"],

        "Occupied Racks":
            output["drivers"]["occupied_racks"],

        "Rack Revenue":
            output["revenue_streams"]["rack_revenue"],

        "OTC Revenue":
            output["revenue_streams"]["otc_revenue"],

        "Power Revenue":
            output["revenue_streams"]["power_revenue"],

        "Seats Revenue":
            output["revenue_streams"]["seats_revenue"],

        "Managed Revenue":
            output["revenue_streams"]["managed_revenue"],

        "Total Revenue":
            output["financials"]["total_revenue"],

        "Net Revenue":
            output["financials"]["net_revenue"],
    })

    print("\n==============================")
    print("REVENUE MODEL TEST")
    print("==============================")

    print("\nYEARS")
    print(output["metadata"]["years"])

    print("\nOCCUPIED RACKS")
    print(output["drivers"]["occupied_racks"])

    print("\nFACILITY LOAD (kW)")
    print(output["drivers"]["facility_load_kw"])

    print("\nNET REVENUE")
    print(output["financials"]["net_revenue"])

    print("\nPOWER REVENUE")
    print(output["revenue_streams"]["power_revenue"])

    print("\nASSUMPTION REGISTER")

    for key, value in output[
        "assumption_register"
    ].items():

        print(f"{key}: {value}")

    print("\nREVENUE TABLE\n")
    print(revenue_df)