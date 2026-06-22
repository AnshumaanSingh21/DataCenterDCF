import json


from src.llm.gemini_provider import (
    generate
)


def extract_with_llm(prompt):

    response = generate(prompt)

    # Strip markdown fences
    response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # Gemini 2.5 Flash may emit thinking tokens before the JSON object.
    # Extract only the content between the outermost { } to handle that.
    start = response.find("{")
    end   = response.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in response: {response[:200]}")

    return json.loads(response[start:end])