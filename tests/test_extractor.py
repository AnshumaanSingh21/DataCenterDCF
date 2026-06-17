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
            "JMF Report",

        "text":
            "The blended average MRR at INR 7.7K per KW."
    }
]

result = extract_assumption(
    "mrr_per_kw",
    context
)

print(result)