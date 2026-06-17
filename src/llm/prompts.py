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