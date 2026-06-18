import json
import sys
from pathlib import Path

project_root = (
    Path(__file__)
    .resolve()
    .parents[2]
)

sys.path.append(str(project_root))

from src.agents.revenue_agent import (
    revenue_agent
)


user_inputs = {

    "location": "Mumbai",

    "total_racks": 1000,

    "facility_type": "retail_colo",

    "projection_years": 10,

    "start_year": 2026,

    "deployment_schedule": {
        0: 300,
        3: 300,
        6: 400
    }
}


output = revenue_agent(user_inputs)


# ----------------------------------------
# CONSOLE SUMMARY
# ----------------------------------------

print("\n" + "=" * 60)
print("REVENUE AGENT — ASSUMPTION PROVENANCE")
print("=" * 60)

for key, prov in output["assumption_provenance"].items():

    tag = (
        "[MARKET] "
        if prov["source"] == "market_agent"
        else "[DEFAULT]"
    )

    print(
        f"{tag}  {key:<35} {prov['value']}"
        f"  (conf={prov['confidence']:.2f})"
    )

print("\n" + "=" * 60)
print("REVENUE SUMMARY (crore)")
print("=" * 60)

rs      = output["revenue_streams"]
years   = output["metadata"]["years"]
occ     = output["drivers"]["occupied_racks"]

print(
    f"\n{'Yr':<6} {'Occ':>6} {'ColoRev':>9} "
    f"{'OTCRev':>8} {'PwrRev':>8} "
    f"{'SeatRev':>8} {'MgdRev':>8} "
    f"{'GrossRev':>10} {'NetRev':>9}"
)

for i in range(len(years)):
    print(
        f"{years[i]:<6} {occ[i]:>6.0f}"
        f" {rs['recurring_colo_revenue'][i]:>9.2f}"
        f" {rs['otc_setup_revenue'][i]:>8.2f}"
        f" {rs['power_revenue'][i]:>8.2f}"
        f" {rs['seats_revenue'][i]:>8.2f}"
        f" {rs['managed_services_revenue'][i]:>8.2f}"
        f" {rs['gross_revenue'][i]:>10.2f}"
        f" {rs['net_revenue'][i]:>9.2f}"
    )


# ----------------------------------------
# FULL JSON DUMP
# ----------------------------------------

output_path = Path("outputs/revenue/revenue_agent_output.json")

output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\nFull JSON written to: {output_path}")
