from pathlib import Path
from typing import Any

import polars as pl

from pitchoune.io import IO


class XLSX_IO(IO):
    """XLSX IO class for reading and writing XLSX files using Polars."""
    def __init__(self):
        super().__init__(suffix="xlsx")

    def deserialize(self, filepath: Path|str, schema=None, sheet_name: str = "sheet1", engine: str = "openpyxl", read_options: dict[str, Any] = None) -> None:
        """Read an XLSX file and return a Polars DataFrame."""
        return pl.read_excel(
            str(filepath),
            schema_overrides=schema,
            sheet_name=sheet_name,
            engine=engine,
            read_options=read_options,
            infer_schema_length=10000
        )

    def serialize(self, df: pl.DataFrame, filepath: Path|str) -> None:
        """Write a Polars DataFrame to an XLSX file."""
        df.write_excel(str(filepath))
