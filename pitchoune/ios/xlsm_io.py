from typing import Any, Iterable
import math
from pathlib import Path as StdPath

import polars as pl

from pitchoune.io import IO


class XLSM_IO(IO):
    """ XLSM IO class that can read and write XLSM files using Polars.
    """
    def __init__(self):
        super().__init__(suffix="xlsm")

    def deserialize(
        self,
        filepath: StdPath|str,
        schema=None,
        sheet_name: str = "sheet1",
        engine: str = "openpyxl",
        read_options: dict[str, Any] = None,
        **params
    ) -> None:
        """ Reads an XLSM file and return a Polars DataFrame """
        df = pl.read_excel(
            str(filepath),
            schema_overrides=schema,
            sheet_name=sheet_name,
            engine=engine,
            read_options=read_options,
            infer_schema_length=10000,
            **params
        )
        df = df.with_columns(
            pl.col(col).str.replace_all("_x000D_", "")
            for col in df.columns if df[col].dtype in (pl.Utf8, pl.String)
        )
        return df

    def serialize(
        self,
        df: pl.DataFrame | str | list[pl.DataFrame | str],
        filepath: str,
        template: str = None,
        sheet_name: str = "Sheet1",
        start_ref: str = "A1",
        sheets: list[str] = None,
        copy_formulas: Iterable[dict[str, str]] = None,
        chunk_size: int = 5000,
        text_columns: list[str] = None,
        n_parts: int = 1
    ) -> None:
        """ Writes a df in a xlsm file based on another xlsm file (to keep the macros and the custom ribbon if any).

                copy_formulas param is used to copy a range of formula to another one (and maybe extend it to last row) :
                    ex: copy_formulas=({"origin_sheet": "origin", "origin_ref": "B2:B2", "dest_sheet": "dest", "dest_ref": "B2:B2", "extend_using_col": "U"},)

                sheets param is used to match return item with sheet and write it at the specified cell :
                    ex: sheets=("Sheet1:A1", "Sheet2:A1", "Sheet3:A1"),

                text_columns param is used to force text format on specific columns to avoid Excel auto-converting values (dates, times, etc.) :
                    ex: text_columns=["SYNTAGMES", "RAW SYNTAGMES"]

                n_parts param splits the first DataFrame into N files named <stem>_partieXofN<suffix> :
                    ex: n_parts=3 → gdico_partie1of3.xlsm, gdico_partie2of3.xlsm, gdico_partie3of3.xlsm
                        n_parts=1 → comportement normal, un seul fichier
        """
        import xlwings as xw
        if isinstance(df, pl.DataFrame) or isinstance(df, str):
            df = (df,)
            sheets = (f"{sheet_name}:{start_ref}",)

        # construction de la liste des parties à écrire : [(df_items, filepath_part), ...]
        if n_parts > 1 and isinstance(df[0], pl.DataFrame):
            base      = StdPath(filepath)
            part_size = math.ceil(df[0].height / n_parts)
            parts = [
                (
                    [df[0].slice((i - 1) * part_size, part_size)] + list(df[1:]),
                    base.parent / f"{base.stem}_partie{i}of{n_parts}{base.suffix}"
                )
                for i in range(1, n_parts + 1)
            ]
        else:
            parts = [(list(df), StdPath(filepath))]

        for df_items, part_path in parts:
            with xw.App(visible=False) as app:
                wb = app.books.open(template if template else str(part_path))

                for item, sheet in zip(df_items, sheets):
                    name, start_ref = sheet.split(":")
                    ws = wb.sheets[name]
                    if isinstance(item, pl.DataFrame):
                        if text_columns:
                            for col in text_columns:
                                if col in item.columns:
                                    col_index = item.columns.index(col) + 1
                                    ws.range((1, col_index), (ws.cells.last_cell.row, col_index)).number_format = '@'
                        data = [item.columns] + item.rows()
                        for i in range(0, len(data), chunk_size):
                            chunk = data[i:i + chunk_size]
                            ws.range(start_ref).offset(i, 0).value = chunk
                        if text_columns:
                            for col in text_columns:
                                if col in item.columns:
                                    col_index = item.columns.index(col) + 1
                                    ws.range((1, col_index), (ws.cells.last_cell.row, col_index)).number_format = '@'
                    elif isinstance(item, str):
                        ws.range(start_ref).value = item
                    elif isinstance(item, list):
                        for i in range(0, len(item), chunk_size):
                            chunk = item[i:i + chunk_size]
                            ws.range(start_ref).offset(i, 0).options(transpose=True).value = chunk

                if copy_formulas is not None:
                    for formula in copy_formulas:
                        origin_sheet     = formula.get("origin_sheet")
                        origin_ref       = formula.get("origin_ref")
                        dest_sheet       = formula.get("dest_sheet")
                        dest_ref         = formula.get("dest_ref")
                        extend_using_col = formula.get("extend_using_col", None)
                        origin = wb.sheets[origin_sheet]
                        dest   = wb.sheets[dest_sheet]
                        if extend_using_col:
                            last_row = dest.range(extend_using_col + str(dest.cells.last_cell.row)).end("up").row
                            dest_ref = f"{dest_ref[:-1]}{last_row}"
                        dest.range(dest_ref).formula = origin.range(origin_ref).formula

                part_path.parent.mkdir(parents=True, exist_ok=True)
                wb.save(str(part_path))
                wb.close()
