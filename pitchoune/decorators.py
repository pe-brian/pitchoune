from typing import Iterable

from pitchoune.dataset import Dataset
from pitchoune.functions import load_file, persist
from pitchoune.injector import injector


def load(name: str, source: str = None, schema: Iterable = None):
    def decorator(function):
        def wrapper(*args, **kwargs):
            ds = Dataset(name=name, data=load_file(source), schema=schema) if source and schema else Dataset(name=name)
            injector.register_arg(function, name, ds)
            return injector.inject(function, *args, **kwargs)
        return wrapper
    return decorator


def save(name: str):
    def decorator(function):
        def wrapper(*args, **kwargs):
            ds = function(*args, **kwargs)
            ds.name = name
            persist(ds)
            return ds
        return wrapper
    return decorator
