from pathlib import Path
from typing import Any
import time

import polars as pl

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
        data: pl.DataFrame | Any,
        filepath: str,
        template: str = None,
        sheet_name: str = "Sheet1",
        start_ref: str = "A1"
    ) -> None:
        """Write a df in a xlsm file based on another xlsm file (to keep the macros and the custom ribbon if any)."""
        import xlwings as xw
        data = [data.columns] + data.rows() if isinstance(data, pl.DataFrame) else data
        # Ouverture Excel invisible pour ne rien casser
        with xw.App(visible=False) as app:
            wb = app.books.open(template if template else filepath, read_only=False, editable=True)
            ws = wb.sheets[sheet_name]
            ws.range(start_ref).value = data
            wb.save(filepath)
