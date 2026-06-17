import os
import pandas as pd


def export_opex_report(
    opex_output,
    file_path
):

    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
    )

    assumptions_df = pd.DataFrame(

        list(
            opex_output[
                "assumption_register"
            ].items()
        ),

        columns=[
            "Assumption",
            "Value"
        ]
    )

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl"
    ) as writer:

        opex_output[
            "dataframes"
        ]["drivers_df"].to_excel(
            writer,
            sheet_name="Opex Inputs",
            index=False
        )

        opex_output[
            "dataframes"
        ]["cost_lines_df"].to_excel(
            writer,
            sheet_name="Opex Costs",
            index=False
        )

        opex_output[
            "dataframes"
        ]["financials_df"].to_excel(
            writer,
            sheet_name="Opex Outputs",
            index=False
        )

        assumptions_df.to_excel(
            writer,
            sheet_name="Opex Assumptions",
            index=False
        )

    print(
        f"\nOpex report exported to:\n{file_path}"
    )