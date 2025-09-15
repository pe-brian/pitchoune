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
        df: pl.DataFrame | str | list[pl.DataFrame | str],
        filepath: str,
        template: str = None,
        sheet_name: str = "Sheet1",
        start_ref: str = "A1",
        sheets: list[str] = None
    ) -> None:
        """
            Write a df in a xlsm file based on another xlsm file (to keep the macros and the custom ribbon if any).
        """
        import xlwings as xw

        # si df n'est pas une liste
        if isinstance(df, pl.DataFrame) or isinstance(df, str):
            df = (df,)
            sheets = (f"{sheet_name}:{start_ref}",)
        
        with xw.App(visible=False) as app:
            wb = app.books.open(template if template else filepath)
            for item, sheet in zip(df, sheets):
                name, start_ref = sheet.split(":")
                ws = wb.sheets[name]
                if isinstance(item, pl.DataFrame):
                    ws.range(start_ref).value = [item.columns] + item.rows()
                elif isinstance(item, str):
                    ws.range(start_ref).value = item
                elif isinstance(item, list):
                    ws.range(start_ref).options(transpose=True).value = item
            wb.save(filepath)
            wb.close()
