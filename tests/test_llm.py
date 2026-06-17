from pathlib import Path
import sys

project_root = (
    Path(__file__)
    .resolve()
    .parents[1]
)

sys.path.append(
    str(project_root)
)

from src.llm.prompts import (
    build_extraction_prompt
)

from src.llm.llm_interface import (
    extract_with_llm
)


context = """
The blended average MRR at INR 7.7K per KW.
"""

prompt = build_extraction_prompt(
    "mrr_per_kw",
    context
)

result = extract_with_llm(
    prompt
)

print(result)

print(
    type(result)
)