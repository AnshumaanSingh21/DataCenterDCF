import json


from src.llm.gemini_provider import (
    generate
)


def extract_with_llm(prompt):

    response = generate(
        prompt
    )

    response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(
        response
    )