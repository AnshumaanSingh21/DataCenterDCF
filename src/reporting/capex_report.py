import os
import pandas as pd


def export_capex_report(
    capex_output,
    file_path
):

    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
    )

    assumptions_df = pd.DataFrame(

        list(
            capex_output[
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

        capex_output[
            "dataframes"
        ]["capex_df"].to_excel(
            writer,
            sheet_name="Capex Projection",
            index=False
        )

        assumptions_df.to_excel(
            writer,
            sheet_name="Capex Assumptions",
            index=False
        )

    print(
        f"\nCapex report exported to:\n{file_path}"
    )
