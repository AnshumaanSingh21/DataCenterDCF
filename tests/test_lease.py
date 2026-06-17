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

from src.extraction.extractor import (
    extract_assumption
)

context = [

    {
        "source":
            "Yotta Investor Presentation",

        "text":
            """
            Average Lease Term
            ~9.5 Years
            """
    }
]

result = extract_assumption(
    "lease_term_years",
    context
)

print(result)