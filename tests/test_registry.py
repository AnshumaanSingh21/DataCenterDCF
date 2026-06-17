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

from src.registry.assumption_registry import (
    create_registry,
    update_registry
)

registry = create_registry()

registry = update_registry(

    registry,

    "mrr_per_kw",

    {
        "value": 7700,
        "source": "JMF",
        "confidence": 1.0,
        "valid": True
    }
)

print(registry)