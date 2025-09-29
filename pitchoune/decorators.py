import functools
import inspect
import json
from pathlib import Path
import sys
from typing import Any, Iterable
import csv

from pitchoune.utils import (
    enrich_path,
    evaluate_rule,
    load_from_conf,
    open_file,
    check_duplicates,
    watch_file
)
from pitchoune import (
    base_io_factory,
    base_chat_factory
)


class StreamFormatNotSupported(Exception):
    """ Raised when the file format is not supported for streaming
    """
    pass

class RequirementsNotSatisfied(Exception):
    """ Raised when one or more required conditions are not met.
    """
    pass


# Input

def input_df(
    filepath: Path|str,
    id_cols: Iterable[str] = None,
    schema = None, proc = None,
    **params
):
    """ Decorator that reads a dataframe from a file and inject it to the decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            df = None
            if filepath is not None:
                new_filepath = Path(filepath)
                try:
                    df = base_io_factory.create(suffix=new_filepath.suffix[1:]).deserialize(new_filepath, schema, **params)
                    if id_cols:
                        check_duplicates(df, *id_cols)  # Check for duplicates in the specified columns
                    if proc:
                        df = proc(df)
                except FileNotFoundError:
                    df = None
            new_args = args + (df,)
            return func(*new_args, **kwargs)
        return wrapper
    return decorator


def input_file(
    filepath: str|Path,
    split_lines: bool=False
):
    """ Decorator that injects a file content into a function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with open(filepath, "r", encoding="utf8") as f:
                value = f.read()
            if split_lines:
                value = value.split("\n")
            new_args = args + (value,)
            return func(*new_args, **kwargs)
        return wrapper
    return decorator


def input_conf_param(
    key: str,
    default_value: Any = None
):
    """ Decorator that injects a chat instance into a function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_key = key
            if ":" not in new_key:
                prefix = "str"
            else:
                prefix, new_key = new_key.split(":", 1)

            # For config keys, retrieve raw value
            value = load_from_conf(new_key, default_value=default_value)

            if value is None:
                value = default_value

            else:
        
                if prefix == "path":
                    value = enrich_path(value)

                elif prefix == "str":
                    pass

                elif prefix == "int":
                    value = int(value)

                elif prefix == "float":
                    value = float(value)

                elif prefix == "list":
                    value = [v for v in value.split(",") if v]

                else:
                    raise Exception("Invalid prefix")

            new_args = args + (value,)

            return func(*new_args, **kwargs)  # Injection of the chat instance into the function
        return wrapper
    return decorator


def read_stream(
    filepath: Path|str,
    recover_progress_filepath: Path|str = None
):
    """ Decorator that streams a .jsonl or .csv file line by line and injects the parsed data into the function.
        Injected kwargs:
          - current_line: line number (starting at 1)
          - total_lines: total number of lines in the file
          - parsed data: dict from JSONL or CSV row
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_filepath = Path(filepath)

            # Count total lines
            if new_filepath.suffix == ".jsonl":
                with open(new_filepath, "r", encoding="utf-8") as f:
                    total_lines = sum(1 for _ in f)
            elif new_filepath.suffix == ".csv":
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=";")
                    total_lines = sum(1 for _ in reader)

            # Determine how many lines to skip (recover progress)
            already_done = 0
            if recover_progress_filepath:
                try:
                    if recover_progress_filepath.suffix == ".jsonl":
                        with open(recover_progress_filepath, "r", encoding="utf-8") as f:
                            already_done = max(sum(1 for _ in f), 0)
                    elif recover_progress_filepath.suffix == ".csv":
                        with open(recover_progress_filepath, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f, delimiter=";")
                            already_done = max(sum(1 for _ in reader), 0)
                except FileNotFoundError:
                    already_done = 0

            def process_line(data: dict, current_line: int):
                injected_kwargs = dict(kwargs)
                injected_kwargs.update(data)
                sig = inspect.signature(func).parameters
                if "current_line" in sig:
                    injected_kwargs["current_line"] = current_line
                if "total_lines" in sig:
                    injected_kwargs["total_lines"] = total_lines
                func(*args, **injected_kwargs)

            suffix = new_filepath.suffix.lower()
            with open(new_filepath, "r", encoding="utf-8-sig") as f:
                if suffix == ".jsonl":
                    for current_line, line in enumerate(f, start=1):
                        if current_line <= already_done:
                            continue
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        process_line(data, current_line)

                elif suffix == ".csv":
                    reader = csv.DictReader(f, delimiter=";")
                    for current_line, row in enumerate(reader, start=1):
                        if current_line <= already_done:
                            continue
                        process_line(row, current_line)

                else:
                    raise StreamFormatNotSupported(f"Unsupported file format: {suffix}")
        return wrapper
    return decorator


# Output


def output(
    filepath: Path|str=None,
    human_check: bool=False,
    checks: list=None,
    **params
):
    """ Decorator that copies the return of the decorated function to a file
    """
    # Compteur global pour tous les décorateurs
    if not hasattr(output, 'counter'):
        output.counter = 0
    
    # Capturer l'index de ce décorateur
    decorator_index = output.counter
    output.counter += 1
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if filepath is not None:
                new_filepath = Path(filepath)
            
            res = func(*args, **kwargs)

            if checks:
                for check in checks:
                    ret = res(check)
                    if ret:
                        raise RequirementsNotSatisfied(ret)
            
            if res is None:
                return res
            
            # Si c'est un tuple, prendre l'élément correspondant à cet index de décorateur
            if isinstance(res, tuple):
                # Calculer l'index inversé pour compenser l'ordre d'exécution des décorateurs
                total_decorators = output.counter
                inverted_index = total_decorators - 1 - decorator_index
                selected_res = res[inverted_index if inverted_index < len(res) else -1]
            else:
                selected_res = res
            
            if filepath is not None:
                base_io_factory.create(suffix=new_filepath.suffix[1:]).serialize(df=selected_res, filepath=new_filepath, **params)
                if human_check:
                    open_file(new_filepath)
                    watch_file(new_filepath)
            
            # Retourner le tuple original pour que les autres décorateurs puissent aussi l'utiliser
            return res
        return wrapper
    return decorator


def write_stream(
    filepath: Path|str
):
    """ Decorator that writes the returned dictionary to a .jsonl or .csv file line by line.
        The decorated function must return a dictionary.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_filepath = Path(filepath)

            data = func(*args, **kwargs)
            if data is None:
                return None

            def write_line(entry: dict):
                if not isinstance(entry, dict):
                    raise ValueError("La fonction décorée doit retourner un dictionnaire.")

                if new_filepath.suffix == ".jsonl":
                    with open(new_filepath, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

                elif new_filepath.suffix == ".csv":
                    file_exists = new_filepath.exists()
                    with open(new_filepath, "a", encoding="utf-8-sig", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=entry.keys(), delimiter=";")
                        if not file_exists:
                            writer.writeheader()
                        writer.writerow(entry)
                else:
                    raise Exception("Unsupported file format for streaming")

            write_line(data)
            return data
        return wrapper
    return decorator


# Chat

def use_chat(
    name: str,
    model: str,
    prompt_filepath: str=None,
    prompt: str=None,
    local: bool=True,
    **extra_params
):
    """ Decorator that injects a chat instance into a function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if prompt_filepath:
                new_prompt_filepath = Path(prompt_filepath)
            new_prompt = prompt  # Get the prompt from the decorator
            if new_prompt is None and prompt_filepath is not None:
                with open(new_prompt_filepath, "r") as f:
                    new_prompt = f.read()
            kwargs[name] = base_chat_factory.create(
                model=model,
                prompt=new_prompt,
                local=local,
                **extra_params
            )  # Get the chat instance
            return func(*args, **kwargs)  # Injection of the chat instance into the function
        return wrapper
    return decorator


# Requirements

def requested(
    *rules: str
):
    """ Decorator that mades a prerequise mandatory
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for rule in rules:
                if rule.startswith("return:"):
                    continue
                if not evaluate_rule(rule):
                    raise RequirementsNotSatisfied(f"Rule not satisfied: {rule}")

            result = func(*args, **kwargs)

            for rule in rules:
                if not rule.startswith("return:"):
                    continue
                _, check_func_name = rule.split(":", 1)
                check_func = globals().get(check_func_name) or getattr(sys.modules[func.__module__], check_func_name)
                if not callable(check_func):
                    raise RequirementsNotSatisfied(f"'{check_func_name}' is not a callable function")
                post_result = check_func(result)
                if post_result is not None:
                    raise RequirementsNotSatisfied(str(post_result))

            return result
        return wrapper
    return decorator
