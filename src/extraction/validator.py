from src.extraction.assumption_schema import (
    ASSUMPTION_DEFINITIONS
)


def validate_assumption(
    assumption_name,
    value
):

    if value is None:

        return False

    schema = (
        ASSUMPTION_DEFINITIONS[
            assumption_name
        ]
    )

    min_value = (
        schema["valid_range"][0]
    )

    max_value = (
        schema["valid_range"][1]
    )

    return (
        min_value
        <= value
        <= max_value
    )