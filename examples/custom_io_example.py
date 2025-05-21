from pitchoune.decorators import input_df, output_df
from pitchoune import base_io_factory

import polars as pl

from pitchoune.io import IO


with open("data/dummy.ploup", "w") as file:
    file.write("a;b\n1;2\n3;4\n5;6\n7;8\n9;10\n11;12\n13;14\n15;16\n17;18\n19;20\n21;22\n23;24\n25;26\n27;28\n29;30")


class Ploup_IO(IO):
    def __init__(self):
        super().__init__(suffix="ploup")

    def deserialize(self, filepath: str, schema=None, separator: str=";", decimal_comma: bool = False) -> None:
        return pl.read_csv(filepath, schema_overrides=schema, encoding="utf-8", separator=separator, decimal_comma=decimal_comma)

    def serialize(self, df: pl.DataFrame, filepath: str, separator: str=";") -> None:
        df.write_csv(filepath, separator=separator, quote_style="non_numeric", include_bom=True)


base_io_factory.register("ploup", Ploup_IO)


@input_df("data/dummy.ploup")
@output_df("data/output.ploup")
def main(df):
    return df


if __name__ == "__main__":
    main()
 