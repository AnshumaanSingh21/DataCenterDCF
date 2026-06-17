from assumptions.capex_defaults import (
    get_default_capex_assumptions
)

from assumptions.loan_defaults import (
    get_default_loan_assumptions
)

from src.engines.capex_engine import (
    compute_capex
)

from src.engines.loan_engine import (
    compute_loan
)


user_inputs = {

    "location": "Mumbai",

    "total_racks": 1000,

    "facility_type": "wholesale",

    "projection_years": 10
}

# ----------------------------------
# CAPEX
# ----------------------------------

capex_output = compute_capex(

    user_inputs,

    get_default_capex_assumptions()
)

# ----------------------------------
# LOAN
# ----------------------------------

loan_output = compute_loan(

    capex_output,

    get_default_loan_assumptions()
)

print("\n==============================")
print("LOAN MODEL TEST")
print("==============================")

print("\nDEBT FUNDING")

print(
    loan_output["capital_structure"]
    ["debt_funding"]
)

print("\nEQUITY FUNDING")

print(
    loan_output["capital_structure"]
    ["equity_funding"]
)

print("\nLONG TERM DEBT ACCOUNT")

print(
    loan_output["dataframes"]
    ["debt_account_df"]
)

print("\nNUMBER OF TRANCHES")

print(
    len(
        loan_output["tranches"]
    )
)

for tranche in loan_output["tranches"]:

    print(
        f"\nTRANCHE {tranche['tranche_id']}"
    )

    print(
        f"Loan Amount: "
        f"{tranche['loan_amount']:.2f}"
    )

    print(
        f"Draw Year: "
        f"{tranche['draw_year']}"
    )