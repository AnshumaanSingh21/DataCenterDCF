from src.extraction.validator import (
    validate_assumption
)

from src.llm.prompts import (
    build_extraction_prompt
)

from src.llm.llm_interface import (
    extract_with_llm
)


def extract_assumption(
    assumption_name,
    context
):

    # --------------------------------
    # Build Context String
    # --------------------------------

    context_text = ""

    for item in context:

        context_text += (
            f"\nSOURCE: {item['source']}\n"
        )

        context_text += (
            item["text"]
        )

        context_text += "\n\n"

    # --------------------------------
    # Build Prompt
    # --------------------------------

    prompt = build_extraction_prompt(
        assumption_name,
        context_text
    )

    # --------------------------------
    # LLM Extraction
    # --------------------------------

    result = extract_with_llm(
        prompt
    )

    value = result.get(
        "value"
    )

    confidence = result.get(
        "confidence",
        0.0
    )

    reasoning = result.get(
        "reasoning",
        ""
    )

    # --------------------------------
    # Source Tracking
    # --------------------------------

    source = None

    if len(context) > 0:

        source = context[0]["source"]

    # --------------------------------
    # Validation
    # --------------------------------

    is_valid = validate_assumption(
        assumption_name,
        value
    )

    if not is_valid:

        value = None

    return {

        "value": value,

        "source": source,

        "confidence": confidence,

        "reasoning": reasoning,

        "valid": is_valid
    }

   