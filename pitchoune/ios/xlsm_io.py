from pathlib import Path
from typing import Any

import polars as pl

import xlwings as xw
from typing import Tuple

from pitchoune.io import IO


class XLSM_IO(IO):
    """XLSM IO class for reading and writing XLSM files using Polars."""
    def __init__(self):
        super().__init__(suffix="xlsm")

    def deserialize(self, filepath: Path|str, schema=None, sheet_name: str = "sheet1", engine: str = "openpyxl", read_options: dict[str, Any] = None, **params) -> None:
        """Read an XLSM file and return a Polars DataFrame."""
        return pl.read_excel(
            str(filepath),
            schema_overrides=schema,
            sheet_name=sheet_name,
            engine=engine,
            read_options=read_options,
            infer_schema_length=10000,
            **params
        )

    def serialize(
        self,
        df: pl.DataFrame,
        filepath: str,
        based_on_filepath: str,
        sheet_name: str = "Sheet1",
        start_ref: str = "A1"
    ) -> None:
        """Write a df in a xlsm file based on another xlsm file (to keep the macros and the custom ribbon if any)."""

        data = [df.columns] + df.rows()

        # Ouverture Excel invisible pour ne rien casser
        app = xw.App(visible=False)
        try:
            wb = app.books.open(based_on_filepath)
            ws = wb.sheets[sheet_name]
            ws.range(start_ref).value = data
            wb.save(filepath)
            wb.close()
        finally:
            app.quit()
