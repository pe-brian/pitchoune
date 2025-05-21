from pathlib import Path

import polars as pl

from pitchoune.io import IO


class JSONL_IO(IO):
    """JSONL IO class for reading and writing JSON Lines files using Polars."""
    def __init__(self):
        super().__init__(suffix="jsonl")

    def deserialize(self, filepath: Path|str, schema=None) -> pl.DataFrame:
        """Read a JSON Lines file and return a Polars DataFrame."""
        return pl.read_ndjson(str(filepath), schema_overrides=schema)

    def serialize(self, df: pl.DataFrame, filepath: Path|str) -> None:
        """Write a Polars DataFrame to a JSON Lines file."""
        df.write_ndjson(str(filepath))
