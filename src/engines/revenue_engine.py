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
    start_year = user_inputs.get("start_year", 2026)

    # Lease-up curve is defined for the base horizon. For a longer
    # horizon, hold the terminal occupancy (a stabilized DC plateaus —
    # it doesn't keep climbing). For a shorter one, slice. This keeps
    # the base-horizon result identical while making it length-safe.
    _curve = assumptions["lease_up_curve"]
    if years <= len(_curve):
        lease_up = _curve[:years]
    else:
        lease_up = _curve + [_curve[-1]] * (years - len(_curve))

    # ---------------------------------
    # LEASE UP
    # ---------------------------------

    occupied_racks = [
        total_racks * x
        for x in lease_up
    ]

    # ---------------------------------
    # DEPLOYMENT CAP
    # Cap occupied by physically deployed
    # racks each year. Default: all racks
    # available from Year 0.
    # ---------------------------------

    deployment_schedule = user_inputs.get(
        "deployment_schedule",
        {0: total_racks}
    )

    cumulative_deployed = []
    running_deployed = 0

    for i in range(years):
        running_deployed += deployment_schedule.get(i, 0)
        cumulative_deployed.append(running_deployed)

    occupied_racks = [
        min(occupied_racks[i], cumulative_deployed[i])
        for i in range(years)
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
        assumptions["rack_price_per_rack_crore"],
        assumptions["rack_price_escalation"],
        years
    )

    otc_fee = escalate(
        assumptions["otc_price_per_new_rack_crore"],
        assumptions["otc_price_escalation"],
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
        assumptions["seat_price_per_seat_crore"],
        assumptions["seat_price_escalation"],
        years
    )

    managed_mrc = escalate(
        assumptions["managed_service_price_per_rack_crore"],
        assumptions["managed_service_escalation"],
        years
    )

    cross_connect_fee = escalate(
        assumptions["cross_connect_fee_per_connection_crore"],
        assumptions["cross_connect_escalation"],
        years
    )

    remote_hands_fee = escalate(
        assumptions["remote_hands_revenue_per_rack_crore"],
        assumptions["remote_hands_escalation"],
        years
    )

    prof_services_fee = escalate(
        assumptions["professional_services_revenue_per_rack_crore"],
        assumptions["professional_services_escalation"],
        years
    )

    dr_services_fee = escalate(
        assumptions["dr_services_revenue_per_rack_crore"],
        assumptions["dr_services_escalation"],
        years
    )

    # ---------------------------------
    # RECURRING COLOCATION REVENUE
    # ---------------------------------

    recurring_colo_revenue = [
        occupied_racks[i]
        * rack_mrc[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # OTC SETUP REVENUE
    # ---------------------------------

    otc_setup_revenue = [
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
        * assumptions["seats_per_rack"]
        for i in range(years)
    ]

    seats_revenue = [
        seats_sold[i]
        * seat_mrc[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # MANAGED SERVICES REVENUE
    # ---------------------------------

    managed_racks = [
        occupied_racks[i]
        * assumptions["managed_services_penetration"]
        for i in range(years)
    ]

    managed_services_revenue = [
        managed_racks[i]
        * managed_mrc[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # CROSS CONNECT REVENUE
    # ---------------------------------

    cross_connect_revenue = [
        occupied_racks[i]
        * assumptions["cross_connect_penetration"]
        * cross_connect_fee[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # REMOTE HANDS REVENUE
    # ---------------------------------

    remote_hands_revenue = [
        occupied_racks[i]
        * assumptions["remote_hands_penetration"]
        * remote_hands_fee[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # PROFESSIONAL SERVICES REVENUE
    # ---------------------------------

    professional_services_revenue = [
        occupied_racks[i]
        * assumptions["professional_services_penetration"]
        * prof_services_fee[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # DR SERVICES REVENUE
    # ---------------------------------

    dr_services_revenue = [
        occupied_racks[i]
        * assumptions["dr_services_penetration"]
        * dr_services_fee[i]
        * 12
        for i in range(years)
    ]

    # ---------------------------------
    # GROSS REVENUE → DOT → NET
    # ---------------------------------

    gross_revenue = [
        recurring_colo_revenue[i]
        + otc_setup_revenue[i]
        + power_revenue[i]
        + seats_revenue[i]
        + managed_services_revenue[i]
        + cross_connect_revenue[i]
        + remote_hands_revenue[i]
        + professional_services_revenue[i]
        + dr_services_revenue[i]
        for i in range(years)
    ]

    dot_deduction = [
        x * assumptions["dot_share_pct"]
        for x in gross_revenue
    ]

    net_revenue = [
        gross_revenue[i] - dot_deduction[i]
        for i in range(years)
    ]

    # ---------------------------------
    # VALIDATIONS
    # ---------------------------------

    assert all(
        occupied_racks[i] <= cumulative_deployed[i]
        for i in range(years)
    ), "Occupied racks exceed deployed capacity"

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
                    start_year,
                    start_year + years
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

            "power_revenue_per_rack": [
                x / divisor
                for x in power_revenue_per_rack
            ]
        },

        "revenue_streams": {

            "recurring_colo_revenue": recurring_colo_revenue,

            "otc_setup_revenue": otc_setup_revenue,

            "power_revenue": power_revenue,

            "seats_revenue": seats_revenue,

            "managed_services_revenue": managed_services_revenue,

            "cross_connect_revenue": cross_connect_revenue,

            "remote_hands_revenue": remote_hands_revenue,

            "professional_services_revenue": professional_services_revenue,

            "dr_services_revenue": dr_services_revenue,

            "gross_revenue": gross_revenue,

            "dot_deduction": dot_deduction,

            "net_revenue": net_revenue
        },

        "power_detail": {

            "power_cost": power_cost,

            "power_margin": power_margin
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

        "Colo Revenue":
            output["revenue_streams"]["recurring_colo_revenue"],

        "OTC Revenue":
            output["revenue_streams"]["otc_setup_revenue"],

        "Power Revenue":
            output["revenue_streams"]["power_revenue"],

        "Seats Revenue":
            output["revenue_streams"]["seats_revenue"],

        "Managed Revenue":
            output["revenue_streams"]["managed_services_revenue"],

        "Cross Connect":
            output["revenue_streams"]["cross_connect_revenue"],

        "Remote Hands":
            output["revenue_streams"]["remote_hands_revenue"],

        "Prof Services":
            output["revenue_streams"]["professional_services_revenue"],

        "DR Services":
            output["revenue_streams"]["dr_services_revenue"],

        "Gross Revenue":
            output["revenue_streams"]["gross_revenue"],

        "Net Revenue":
            output["revenue_streams"]["net_revenue"],
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
    print(output["revenue_streams"]["net_revenue"])

    print("\nPOWER REVENUE")
    print(output["revenue_streams"]["power_revenue"])

    print("\nASSUMPTION REGISTER")

    for key, value in output[
        "assumption_register"
    ].items():

        print(f"{key}: {value}")

    print("\nREVENUE TABLE\n")
    print(revenue_df)