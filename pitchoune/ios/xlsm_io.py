from pathlib import Path
from typing import Any

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

    def serialize(self, df: pl.DataFrame, filepath: Path|str, **params) -> None:
        """Write a Polars DataFrame to an XLSM file."""
        raise NotImplementedError("XLSM serialization is not supported by Pitchoune. Use XLSX instead.")
