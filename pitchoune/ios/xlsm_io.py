from pathlib import Path
from typing import Any, Iterable

import polars as pl

from pitchoune.io import IO


class XLSM_IO(IO):
    """ XLSM IO class hat can read and write XLSM files using Polars.
    """
    def __init__(
        self
    ):
        super().__init__(suffix="xlsm")

    def deserialize(
        self,
        filepath: Path|str,
        schema=None,
        sheet_name: str = "sheet1",
        engine: str = "openpyxl",
        read_options: dict[str,
        Any] = None,
        **params
    ) -> None:
        """ Reads an XLSM file and return a Polars DataFrame
        """
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
        sheets: list[str] = None,
        copy_formulas: Iterable[dict[str, str]] = None
    ) -> None:
        """ Writes a df in a xlsm file based on another xlsm file (to keep the macros and the custom ribbon if any).

                copy_formulas param is used to copy a range of formula to another one (and maybe extend it to last row) :
                    ex: copy_formulas=({"origin_sheet": "origin", "origin_ref": "B2:B2", "dest_sheet": "dest", "dest_ref": "B2:B2", "extend_using_col": "U"},)

                sheets param is used to match return item with sheet and write it at the specified cell :
                    ex: sheets=("Sheet1:A1", "Sheet2:A1", "Sheet3:A1"),
        """
        import xlwings as xw

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
                
            if copy_formulas is not None:

                for formula in copy_formulas:
                    origin_sheet = formula.get("origin_sheet")
                    origin_ref = formula.get("origin_ref")
                    dest_sheet = formula.get("dest_sheet")
                    dest_ref = formula.get("dest_ref")
                    extend_using_col = formula.get("extend_using_col", None)
                    origin = wb.sheets[origin_sheet]
                    dest = wb.sheets[dest_sheet]
                    if extend_using_col:
                        last_row = dest.range(extend_using_col + str(dest.cells.last_cell.row)).end("up").row
                        dest_ref = f"{dest_ref[:-1]}{last_row}"
                    dest.range(dest_ref).formula = origin.range(origin_ref).formula

            wb.save(filepath)
            wb.close()
