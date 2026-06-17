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