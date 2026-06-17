from pathlib import Path
import sys
import json

# ---------------------------------
# Add project root
# ---------------------------------

project_root = (
    Path(__file__)
    .resolve()
    .parents[2]
)

sys.path.append(
    str(project_root)
)

# ---------------------------------
# Imports
# ---------------------------------

from src.rag.retriever import retrieve
from src.extraction.extractor import (
    extract_assumption
)


def market_agent(location):

    query = (
        f"{location} colocation pricing"
    )

    results = retrieve(
        query,
        k=10
    )

    # --------------------------------
    # Relevance Filter
    # --------------------------------

    relevant_results = []

    keywords = [
        "mrr",
        "pricing",
        "colocation",
        "rack",
        "revenue",
        "lease",
        "term"
    ]

    for result in results:

        text = (
            result.page_content
            .lower()
        )

        if any(
            keyword in text
            for keyword in keywords
        ):

            relevant_results.append(
                result
            )

    # --------------------------------
    # Build Context
    # --------------------------------

    context = []

    for result in relevant_results:

        context.append({

            "source":
                result.metadata.get(
                    "source_file",
                    "Unknown"
                ),

            "text":
                result.page_content[:1000]
        })

    # --------------------------------
    # Save Retrieved Context
    # --------------------------------

    with open(
        "outputs/market_context.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            context,
            f,
            indent=4,
            ensure_ascii=False
        )
    # --------------------------------
    # Market Assumptions
    # --------------------------------
    from src.registry.market_registry import (
    MARKET_ASSUMPTIONS
    )

    

    # --------------------------------
    # Extract Assumptions
    # --------------------------------

    output = {}

    for assumption in MARKET_ASSUMPTIONS:

        output[
            assumption
        ] = extract_assumption(
            assumption,
            context
        )

    return output


if __name__ == "__main__":

    result = market_agent(
        "Mumbai"
    )

    print("\nMarket Agent Output:")
    print("=" * 50)

    print(result)


