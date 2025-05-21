from pathlib import Path

import polars as pl

from pitchoune.io import IO


class TSV_IO(IO):
    """TSV IO class for reading and writing TSV files using Polars."""
    def __init__(self):
        super().__init__(suffix="tsv")

    def deserialize(self, filepath: Path|str, schema=None, separator: str="\t", decimal_comma: bool = False) -> None:
        """Read a TSV file and return a Polars DataFrame."""
        return pl.read_csv(str(filepath), schema_overrides=schema, encoding="utf-8", separator=separator, decimal_comma=decimal_comma)

    def serialize(self, df: pl.DataFrame, filepath: Path|str, separator: str="\t") -> None:
        """Write a Polars DataFrame to a TSV file."""
        df.write_csv(str(filepath), separator=separator, quote_style="non_numeric", include_bom=True)
