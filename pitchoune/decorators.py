import functools
import inspect
import json
import os
from pathlib import Path
from typing import Iterable

from pitchoune.utils import complete_path_with_workdir, open_file, to_path, check_duplicates, get_main_module_name, is_only_extension, watch_file
from pitchoune import base_io_factory, base_chat_factory


def input_df(filepath: Path|str, id_cols: Iterable[str] = None, schema = None, exec_before = None, **params):
    """Decorator for reading a dataframe from a file"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            workdir = to_path(os.getenv("PITCHOUNE_WORKDIR", ""))
            new_filepath = workdir / to_path(filepath) if workdir else to_path(filepath)
            if exec_before:
                new_filepath = exec_before(new_filepath)
            df = base_io_factory.create(suffix=new_filepath.suffix[1:]).deserialize(new_filepath, schema, **params)
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
            workdir = to_path(os.getenv("PITCHOUNE_WORKDIR", ""))
            new_filepath = (get_main_module_name() + filepath) if is_only_extension(filepath) else filepath
            new_filepath = workdir / to_path(new_filepath) if workdir else to_path(new_filepath)
            df = func(*args, **kwargs)
            base_io_factory.create(suffix=new_filepath.suffix[1:]).serialize(df, new_filepath, **params)
            if human_check:
                open_file(new_filepath)  # Open the file for modification
                watch_file(new_filepath)  # Wait for the file to be modified
            return df
        return wrapper
    return decorator


def read_stream(filepath: Path|str, recover_progress_from: Path|str=None):
    """Decorator that reads a JSONL file line by line and injects the data into the function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            already_done = 0
            new_filepath = complete_path_with_workdir(filepath)
            with open(new_filepath, "r", encoding="utf-8") as f:  # Compute the total number of lines
                total_lines = sum(1 for _ in f)
            if recover_progress_from:
                new_recover_progress_from = complete_path_with_workdir(recover_progress_from)
                try:
                    with open(new_recover_progress_from, "r", encoding="utf-8") as f:
                        already_done = sum(1 for _ in f)
                except FileNotFoundError:
                    already_done = 0
            with open(new_filepath, "r", encoding="utf-8") as f:  # Reading and processing the JSONL file
                for current_line, line in enumerate(f, start=1):
                    if already_done > 0:
                        if current_line <= already_done:
                            continue  # Skip lines until we reach the desired start line
                    if new_filepath.suffix == ".jsonl":
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
            new_filepath = (get_main_module_name() + filepath) if is_only_extension(filepath) else filepath
            new_filepath = complete_path_with_workdir(new_filepath)
            data = func(*args, **kwargs)  # Calling the decorated function
            if data is None:
                return data
            if isinstance(data, dict):  # Check if the returned value is a dictionary
                with open(new_filepath, "a", encoding="utf-8") as f:
                    if new_filepath.suffix == ".jsonl":
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
                workdir = to_path(os.getenv("PITCHOUNE_WORKDIR", ""))
                new_filepath = workdir / to_path(prompt_filepath) if workdir else to_path(prompt_filepath)
                with open(new_filepath, "r") as f:
                    new_prompt = f.read()
            kwargs[name] = base_chat_factory.create(name=name, model=model, prompt=new_prompt, local=local)  # Get the chat instance
            return func(*args, **kwargs)  # Injection of the chat instance into the function
        return wrapper
    return decorator
