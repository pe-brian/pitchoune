from pathlib import Path
from typing import Any

import polars as pl

from pitchoune.io import IO


class XLSX_IO(IO):
    """ XLSX IO class that can read and write XLSX files using Polars
    """
    def __init__(
        self
    ):
        super().__init__(suffix="xlsx")

    def deserialize(
        self,
        filepath: Path|str,
        schema=None,
        sheet_name: str = None,
        engine: str = "openpyxl",
        read_options: dict[str, Any] = None,
        **params
    ) -> None:
        """ Reads an XLSX file and return a Polars DataFrame
        """
        return pl.read_excel(
            str(filepath),
            schema_overrides=schema,
            sheet_name=sheet_name,
            sheet_id=1 if sheet_name is None else None,
            engine=engine,
            read_options=read_options,
            infer_schema_length=10000,
            **params
        )

    def serialize(self,
    df: pl.DataFrame, filepath: Path|str, **params) -> None:
        """ Writes a Polars DataFrame to an XLSX file
        """
        df.write_excel(str(filepath), **params)
