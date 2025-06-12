from pitchoune.factory import Factory
from pitchoune.io import IO
from pitchoune.ios.csv_io import CSV_IO
from pitchoune.ios.jsonl_io import JSONL_IO
from pitchoune.ios.tsv_io import TSV_IO
from pitchoune.ios.xlsx_io import XLSX_IO
from pitchoune.ios.xlsm_io import XLSM_IO


class IOFactory(Factory):
    """Factory class to create deserializer instances."""
    def __init__(self):
        self._ios = {
            "jsonl": JSONL_IO,
            "xlsx": XLSX_IO,
            "csv": CSV_IO,
            "tsv": TSV_IO,
            "xlsm": XLSM_IO
        }
        super().__init__(base_class=IO)

    def create(self, *args, suffix: str, **kwargs):
        """Create an instance of the specified IO class."""
        if suffix not in self._ios:
            raise ValueError(f"Unsupported file type: {suffix}. Supported types are: {', '.join(self._ios.keys())}")
        cls = self._ios[suffix]
        return super().create(cls, *args, **kwargs)
    
    def register(self, suffix: str, cls: IO):
        """Register a new IO class with a specific suffix."""
        self._ios[suffix] = cls
