from pathlib import Path

import polars as pl

from pitchoune.io import IO


class CSV_IO(IO):
    """CSV IO class for reading and writing CSV files using Polars."""
    def __init__(self):
        super().__init__(suffix="csv")

    def deserialize(self, filepath: Path|str, schema=None, separator: str=";", decimal_comma: bool = False, encoding: str="utf-8", **params) -> None:
        """Read a CSV file and return a Polars DataFrame."""
        return pl.read_csv(str(filepath), schema_overrides=schema, encoding=encoding, separator=separator, decimal_comma=decimal_comma, **params)

    def serialize(self, df: pl.DataFrame, filepath: Path|str, separator: str=";", **params) -> None:
        """Write a Polars DataFrame to a CSV file."""
        df.write_csv(str(filepath), separator=separator, quote_style="non_numeric", include_bom=True, **params)
