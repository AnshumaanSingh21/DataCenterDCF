from src.extraction.assumption_schema import (
    ASSUMPTION_DEFINITIONS
)


def build_extraction_prompt(
    assumption_name,
    context
):

    assumption = (
        ASSUMPTION_DEFINITIONS[
            assumption_name
        ]
    )

    description = (
        assumption["description"]
    )

    unit = (
        assumption["unit"]
    )

    valid_range = (
        assumption["valid_range"]
    )

    return f"""
You are a financial assumptions extraction engine.

Assumption Name:
{assumption_name}

Description:
{description}

Unit:
{unit}

Expected Range:
{valid_range[0]} to {valid_range[1]}

Context:

{context}

Instructions:

1. Extract the most relevant value.
2. Convert units if necessary.
3. If no reliable value exists, return null.
4. Confidence should be between 0 and 1.
5. Return ONLY valid JSON.

Format:

{{
    "value": number_or_null,
    "confidence": number_between_0_and_1,
    "reasoning": "short explanation"
}}
"""


def build_batch_extraction_prompt(
    location,
    facility_type,
    context_text,
    assumption_names,
    kw_per_rack=None
):

    assumption_block = ""

    for i, name in enumerate(assumption_names, start=1):

        defn = ASSUMPTION_DEFINITIONS[name]

        assumption_block += (
            f"{i}. {name}\n"
            f"   Description : {defn['description']}\n"
            f"   Unit        : {defn['unit']}\n"
            f"   Valid range : {defn['valid_range'][0]} to {defn['valid_range'][1]}\n\n"
        )

    keys_json = (
        "{\n"
        + ",\n".join(
            f'  "{name}": {{"value": <number_or_null>, "confidence": <0.0_to_1.0>, "reasoning": "<one line>"}}'
            for name in assumption_names
        )
        + "\n}"
    )

    density_line = (
        f"Rack density   : {kw_per_rack} kW per rack "
        f"(use EXACTLY this value for any per-kW → per-rack conversions)"
        if kw_per_rack is not None
        else ""
    )

    return f"""You are a financial data extraction engine for an Indian data center investment model.

Location      : {location}
Facility type : {facility_type}
{density_line}

---
MARKET RESEARCH CONTEXT
{context_text}
---

Extract the following assumptions from the context above.

Rules:
- All monetary values must be in Indian Rupees (INR).
- Return the value in the unit specified for each assumption.
- Confidence 1.0 = explicitly stated in context. 0.0 = not found.
- If the context contains no reliable data for an assumption, set value to null.
- Do NOT guess. Prefer null over a fabricated number.
- If the source data is in ₹/kW/month and you need ₹/rack/month, multiply by the
  rack density stated above — do NOT use values from the context or your own knowledge.
- Return ONLY valid JSON — no markdown, no explanation outside the JSON.

Assumptions to extract:

{assumption_block}
Expected output format:
{keys_json}
"""
