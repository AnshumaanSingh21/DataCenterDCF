from pathlib import Path
import sys
import json

project_root = (
    Path(__file__)
    .resolve()
    .parents[2]
)

sys.path.append(str(project_root))

from src.rag.retriever import retrieve

from src.registry.market_registry import (
    MARKET_ASSUMPTIONS
)

from src.extraction.batch_extractor import (
    extract_batch_assumptions
)

from assumptions.revenue_defaults import (
    FACILITY_TYPE_OVERRIDES,
    DEFAULT_REVENUE_ASSUMPTIONS
)


def market_agent(location, facility_type="retail_colo", total_racks=1000, kw_per_rack=6.0):

    total_mw = round(total_racks * kw_per_rack / 1000, 1)

    # --------------------------------
    # RAG Retrieval
    # --------------------------------

    query = (
        f"{location} data center colocation "
        f"{total_racks} rack {total_mw}MW "
        f"pricing rack rental power tariff electricity"
    )

    results = retrieve(query, k=10)

    # --------------------------------
    # Relevance Filter
    # --------------------------------

    keywords = [
        "pricing", "colocation", "rack",
        "power", "tariff", "lease", "revenue",
        "rental", "mrc", "electricity"
    ]

    relevant = [
        r for r in results
        if any(
            kw in r.page_content.lower()
            for kw in keywords
        )
    ]

    # --------------------------------
    # Build Context
    # --------------------------------

    context = [
        {
            "source": r.metadata.get(
                "source_file", "Unknown"
            ),
            "text": r.page_content[:1000]
        }
        for r in relevant
    ]

    with open(
        "outputs/market_context.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(context, f, indent=4, ensure_ascii=False)

    # --------------------------------
    # Resolve kw_per_rack from facility
    # overrides so the LLM uses the same
    # density as the revenue engine.
    # --------------------------------

    overrides = FACILITY_TYPE_OVERRIDES.get(
        facility_type, {}
    )

    kw_per_rack = overrides.get(
        "kw_per_rack",
        DEFAULT_REVENUE_ASSUMPTIONS["kw_per_rack"]
    )

    # --------------------------------
    # Batch Extraction (single LLM call)
    # --------------------------------

    output = extract_batch_assumptions(
        assumption_names=MARKET_ASSUMPTIONS,
        context=context,
        location=location,
        facility_type=facility_type,
        kw_per_rack=kw_per_rack,
        total_racks=total_racks,
        total_mw=total_mw
    )

    return output


if __name__ == "__main__":

    result = market_agent("Mumbai", "retail_colo")

    print("\nMarket Agent Output:")
    print("=" * 50)

    for key, val in result.items():
        print(f"\n{key}")
        print(f"  value      : {val['value']}")
        print(f"  confidence : {val['confidence']}")
        print(f"  source     : {val['source']}")
        print(f"  valid      : {val['valid']}")
        print(f"  reasoning  : {val['reasoning']}")
