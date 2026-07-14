# NOTE: not part of the live application. Used only by the standalone
# build_registry.py script and tests/test_registry.py. The live app sources
# market values per-request via src/agents/market_agent.py (see main.py's
# _build_inputs), which does not read from this registry.

from copy import deepcopy

from src.schemas.master_schema import (
    MASTER_SCHEMA
)


def create_registry():

    return deepcopy(
        MASTER_SCHEMA
    )


def update_registry(
    registry,
    assumption_name,
    assumption_data
):

    registry[
        assumption_name
    ] = assumption_data

    return registry