from pathlib import Path
import sys

project_root = (
    Path(__file__)
    .resolve()
    .parents[2]
)

sys.path.append(str(project_root))

from assumptions.revenue_defaults import (
    get_default_revenue_assumptions
)

from src.agents.market_agent import (
    market_agent
)

from src.engines.revenue_engine import (
    compute_revenue
)


CONFIDENCE_THRESHOLD = 0.5


def revenue_agent(user_inputs):

    location = user_inputs["location"]

    facility_type = user_inputs.get(
        "facility_type",
        "retail_colo"
    )

    # --------------------------------
    # Step 1: Market Assumptions
    # --------------------------------

    market_results = market_agent(
        location,
        facility_type
    )

    # --------------------------------
    # Step 2: Start from Defaults
    # --------------------------------

    assumptions = (
        get_default_revenue_assumptions()
    )

    # --------------------------------
    # Step 3: Merge Market → Defaults
    # Market wins if value is valid and
    # confidence meets the threshold.
    # --------------------------------

    provenance = {}

    for key, result in market_results.items():

        value = result["value"]
        confidence = result["confidence"]

        if (
            value is not None
            and confidence >= CONFIDENCE_THRESHOLD
        ):

            assumptions[key] = value

            provenance[key] = {
                "source": "market_agent",
                "value": value,
                "confidence": confidence,
                "reasoning": result["reasoning"]
            }

        else:

            provenance[key] = {
                "source": "default",
                "value": assumptions[key],
                "confidence": 1.0,
                "reasoning": (
                    "RAG extraction returned null "
                    "or below confidence threshold"
                )
            }

    # --------------------------------
    # Step 4: Run Revenue Engine
    # --------------------------------

    revenue_output = compute_revenue(
        user_inputs,
        assumptions
    )

    revenue_output["assumption_provenance"] = (
        provenance
    )

    return revenue_output


if __name__ == "__main__":

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

    print("\n==============================")
    print("REVENUE AGENT OUTPUT")
    print("==============================")

    print("\nASSUMPTION PROVENANCE")
    print("-" * 40)

    for key, prov in output[
        "assumption_provenance"
    ].items():

        tag = (
            "[MARKET]"
            if prov["source"] == "market_agent"
            else "[DEFAULT]"
        )

        print(
            f"{tag} {key}: {prov['value']}"
            f"  (conf={prov['confidence']:.2f})"
        )

    print("\nNET REVENUE (crore)")
    print(output["revenue_streams"]["net_revenue"])

    print("\nOCCUPIED RACKS")
    print(output["drivers"]["occupied_racks"])
