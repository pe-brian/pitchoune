from typing import Any, Tuple
from chocolatine import Query, QueryMode, Col as _

from pitchoune.functions import translate_schema


class Dataset:

    def __init__(self, name: str = None, data: Tuple[Tuple] = None, schema: Tuple = None) -> None:
        self.name = name
        if name and data and schema:
            self._creation_query = Query(query_mode=QueryMode.Create, table=name, cols=[_(name=n, type=t) for n, t in zip(data[0], translate_schema(schema))]).build()
    
    def __str__(self) -> str:
        return f"Dataset(name={self.name or 'Unnamed'})"
    
    def __repr__(self) -> str:
        return f"Dataset(name={self.name or 'Unnamed'})"
    
    def merge(self, other, on=None):
        return self
