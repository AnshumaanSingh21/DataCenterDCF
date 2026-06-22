import os

from dotenv import load_dotenv

import google.generativeai as genai


load_dotenv()


genai.configure(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)


model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

_generation_config = genai.types.GenerationConfig(
    temperature=0.0,   # deterministic — same input always gives same output
    top_p=1.0,
    top_k=1,
)


def generate(prompt):

    response = model.generate_content(
        prompt,
        generation_config=_generation_config,
    )

    return response.text