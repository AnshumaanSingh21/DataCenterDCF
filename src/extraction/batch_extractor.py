from src.extraction.assumption_schema import (
    ASSUMPTION_DEFINITIONS
)

from src.llm.prompts import (
    build_batch_extraction_prompt
)

from src.llm.llm_interface import (
    extract_with_llm
)


def extract_batch_assumptions(
    assumption_names,
    context,
    location,
    facility_type,
    kw_per_rack=None,
    total_racks=None,
    total_mw=None
):
    """
    Single LLM call to extract all assumption_names
    from context. Returns a dict keyed by assumption
    name, each value being {value, confidence, reasoning,
    source, valid}.
    """

    # --------------------------------
    # Build context string
    # --------------------------------

    context_text = ""

    for item in context:

        context_text += (
            f"\nSOURCE: {item['source']}\n"
            f"{item['text']}\n\n"
        )

    # --------------------------------
    # Single LLM call
    # --------------------------------

    prompt = build_batch_extraction_prompt(
        location=location,
        facility_type=facility_type,
        context_text=context_text,
        assumption_names=assumption_names,
        kw_per_rack=kw_per_rack,
        total_racks=total_racks,
        total_mw=total_mw
    )

    raw = extract_with_llm(prompt)

    # --------------------------------
    # Validate and package each result
    # --------------------------------

    results = {}

    source = (
        context[0]["source"]
        if context
        else "unknown"
    )

    for name in assumption_names:

        entry = raw.get(name, {})

        value = entry.get("value")

        confidence = entry.get("confidence", 0.0)

        reasoning = entry.get("reasoning", "")

        valid = _validate(name, value)

        if not valid:
            value = None

        results[name] = {
            "value": value,
            "confidence": confidence,
            "reasoning": reasoning,
            "source": source,
            "valid": valid
        }

    return results


def _validate(name, value):

    if value is None:
        return False

    defn = ASSUMPTION_DEFINITIONS.get(name)

    if defn is None:
        return False

    lo, hi = defn["valid_range"]

    return lo <= value <= hi
