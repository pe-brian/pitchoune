import functools
import inspect
import json
from pathlib import Path
from typing import Any, Iterable

from pitchoune.utils import (
    enrich_path,
    open_file,
    check_duplicates,
    watch_file
)
from pitchoune import (
    base_io_factory,
    base_chat_factory
)


def input_df(filepath: Path|str, id_cols: Iterable[str] = None, schema = None, **params):
    """Decorator for reading a dataframe from a file"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            enriched_filepath = enrich_path(filepath)
            df = None
            if enriched_filepath:
                df = base_io_factory.create(suffix=enriched_filepath.suffix[1:]).deserialize(enriched_filepath, schema, **params)
                if id_cols:
                    check_duplicates(df, *id_cols)  # Check for duplicates in the specified columns
            new_args = args + (df,)
            return func(*new_args, **kwargs)
        return wrapper
    return decorator


def output_df(filepath: Path|str, human_check: bool=False, **params):
    """Decorator for writing a dataframe to a file"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            enriched_filepath = enrich_path(filepath)
            df = None
            if enriched_filepath:
                df = func(*args, **kwargs)
                base_io_factory.create(suffix=enriched_filepath.suffix[1:]).serialize(df, enriched_filepath, **params)
                if human_check:
                    open_file(enriched_filepath)  # Open the file for modification
                    watch_file(enriched_filepath)  # Wait for the file to be modified
            return df
        return wrapper
    return decorator


def output_dfs(*outputs: dict[str, Any]):
    """
        Decorator for writing multiple dataframes to multiple files with individual parameters.
        
        Each argument should be a dict containing:
        - 'filepath': Path or str
        - Optional: 'human_check': bool
        - Optional: any other serialization params
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            dfs = func(*args, **kwargs)
            if not isinstance(dfs, (list, tuple)):
                raise TypeError("Function must return a list or tuple of DataFrames")
            if len(dfs) != len(outputs):
                raise ValueError("Number of outputs must match number of returned DataFrames")
            for df, output_params in zip(dfs, outputs):
                if df is not None:
                    filepath = output_params.pop("filepath")
                    enriched_filepath = enrich_path(filepath)
                    if enriched_filepath:
                        human_check = output_params.pop("human_check", False)
                        suffix = enriched_filepath.suffix[1:]
                        base_io_factory.create(suffix=suffix).serialize(df, enriched_filepath, **output_params)
                        if human_check:
                            open_file(enriched_filepath)
                            watch_file(enriched_filepath)
            return dfs
        return wrapper
    return decorator


def read_stream(filepath: Path|str, recover_progress_from: Path|str=None):
    """Decorator that reads a JSONL file line by line and injects the data into the function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            already_done = 0
            enriched_filepath = enrich_path(filepath)
            if not enriched_filepath:
                raise Exception("Unable to read data from '{filepath}' !")
            with open(enriched_filepath, "r", encoding="utf-8") as f:  # Compute the total number of lines
                total_lines = sum(1 for _ in f)
            if recover_progress_from:
                try:
                    with open(enrich_path(recover_progress_from), "r", encoding="utf-8") as f:
                        already_done = sum(1 for _ in f)
                except FileNotFoundError:
                    already_done = 0
            with open(enriched_filepath, "r", encoding="utf-8") as f:  # Reading and processing the JSONL file
                for current_line, line in enumerate(f, start=1):
                    if already_done > 0:
                        if current_line <= already_done:
                            continue  # Skip lines until we reach the desired start line
                    if enriched_filepath.suffix == ".jsonl":
                        data = json.loads(line)  # Cast the line to a dictionary
                        kwargs |= data
                        if "total_lines" in inspect.signature(func).parameters:
                            kwargs["total_lines"] = total_lines
                        if "current_line" in inspect.signature(func).parameters:
                            kwargs["current_line"] = current_line
                        func(*args, **kwargs)
                    else:
                        raise Exception("File can't be streamed")
        return wrapper
    return decorator


def write_stream(filepath: Path|str):
    """Decorator that writes a dictionary to a JSONL file line by line"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            enriched_filepath = enrich_path(filepath)
            if not enriched_filepath:
                raise Exception("Unable to write data to '{filepath}' !")
            data = func(*args, **kwargs)  # Calling the decorated function
            if data is None:
                return data
            if isinstance(data, dict):  # Check if the returned value is a dictionary
                with open(enriched_filepath, "a", encoding="utf-8") as f:
                    if enriched_filepath.suffix == ".jsonl":
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    else:
                        raise Exception("File can't receive stream")
            else:
                raise ValueError("La fonction décorée doit retourner un dictionnaire.")
            return data
        return wrapper
    return decorator


def use_chat(name: str, model: str, prompt_filepath: str=None, prompt: str=None, local: bool=True):
    """Decorator for injecting a chat instance into a function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_prompt = prompt  # Get the prompt from the decorator
            if new_prompt is None:
                with open(enrich_path(prompt_filepath), "r") as f:
                    new_prompt = f.read()
            kwargs[name] = base_chat_factory.create(name=name, model=model, prompt=new_prompt, local=local)  # Get the chat instance
            return func(*args, **kwargs)  # Injection of the chat instance into the function
        return wrapper
    return decorator
