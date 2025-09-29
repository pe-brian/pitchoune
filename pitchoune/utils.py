import os
import pathlib
import re
import shutil
import sys
import time
import subprocess
import platform
from typing import (
    Any,
    Generator
)

import polars as pl


class RequirementsNotSatisfied(Exception):
    """ Raised when one or more required conditions are not met.
    """
    pass


# polars

def check_duplicates(
    df: pl.DataFrame,
    *id_cols: str
) -> None:
    """ Throws an error if duplicates are found in the dataframe.
    """
    duplicates = df.group_by(id_cols).len().filter(pl.col("count") > 1)
    if len(duplicates) > 0:
        raise ValueError(f"Des doublons ont été trouvés :\n{duplicates}")


def to_path(
    value: pathlib.Path|str
) -> pathlib.Path:
    """ Casts a string to a pathlib.Path object if it's a string.
    """
    return value if isinstance(value, pathlib.Path) else pathlib.Path(value)


# files

def replace_in_file(
    filepath: pathlib.Path,
    repl_mapping: dict[str, str],
    file_suffix: str = "~"
) -> pathlib.Path:
    """ Replaces expressions in a file and saves the result to a new file.
    """
    with open(str(filepath), "r", encoding="utf8") as f:
        data = f.read()
    for text_to_replace, replaced_by in repl_mapping.items():
        new_data = data.replace(text_to_replace, replaced_by)
    new_filepath = filepath.with_name(f"{filepath.stem}~{filepath.suffix}") if file_suffix else filepath
    with open(str(new_filepath), "w", encoding="utf8") as f:
        f.write(new_data)
    return new_filepath


def watch_file(
    filepath: str
):
    """ Watches a file for changes and return when it is modified.
    """
    last_modif = os.path.getmtime(filepath)
    while True:
        time.sleep(2)  # Attente avant de vérifier à nouveau
        new_modif = os.path.getmtime(filepath)
        if new_modif != last_modif:
            break


def open_file(
    file_path
):
    """ Opens the given file with its default editor.
    """
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", file_path])
    else:  # Linux
        subprocess.run(["xdg-open", file_path])


# Path

def replace_home_token_by_home_path(
    path: str
) -> str:
    """ Replace <HOME> by home path
    """
    return path.replace("<HOME>", get_home_path())


def replace_name_token_by_workdir_name(
    path: str
) -> str:
    """ Replace <NAME> by workdir name
    """
    return path.replace("<NAME>", get_workdir_name())


def get_home_path() -> str:
    """ Get the home path
    """
    return str(pathlib.Path.home())


def get_workdir_name() -> str:
    """ Get the home path
    """
    return str(pathlib.Path(os.getenv("PITCHOUNE_WORKDIR")).name)


def extract_subfolder_contents(
    parent_folder: str
) -> None:
    """ Moves contents from a uniquely named subfolder to `parent_folder` and deletes the subfolder if empty.
    """
    subfolders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]  # Get subfolders inside parent_folder
    if len(subfolders) == 1 and subfolders[0] == os.path.basename(parent_folder):  # Ensure there is **only one** subfolder and its name matches `parent_folder`
        subfolder_path = os.path.join(parent_folder, subfolders[0])
        for item in os.listdir(subfolder_path):  # Move all contents to parent folder
            shutil.move(os.path.join(subfolder_path, item), parent_folder)
        os.rmdir(subfolder_path)  # Remove the now-empty subfolder


def iter_all_files(
    root_folder: pathlib.Path|str
) -> Generator[pathlib.Path, None, None]:
    """ Recursively yields file paths inside subdirectories of `root_folder`.
    """
    for folder, _, files in os.walk(root_folder):
        for file in files:
            yield pathlib.Path(os.path.join(folder, file))  # Yield file paths one by one


def is_only_extension(
    path: str
) -> bool:
    """ Check if the path has only one component and is a file extension.
    """
    return len(path) > 1 and path[0] == '.' and "/" not in path


def change_suffix(
    filepath: str,
    new_suffix: str
):
    """ Change the file extension while preserving the original name.
    """
    filepath = pathlib.Path(filepath)
    filepath = filepath.with_suffix(new_suffix)
    return filepath


def complete_path_with_workdir(
    filepath: str|pathlib.Path
) -> pathlib.Path:
    """ Complete the file path with the pitchoune working directory.
    """
    workdir = os.getenv("PITCHOUNE_WORKDIR")
    return workdir / to_path(filepath) if workdir and not os.path.isabs(filepath) else to_path(filepath)


def replace_conf_key_by_conf_value(
    filepath: str
) -> str:
    """ Replace conf: by conf value
    """
    if filepath.startswith("conf:"):
        return load_from_conf(filepath.removeprefix("conf:"))
    return filepath


def replace_by_module_name_if_only_extension(
    filepath: str
):
    """ Replace for example .xlsx by example.xlsx if the main module name is example
    """
    return (get_main_module_name() + filepath) if is_only_extension(filepath) else filepath


def load_from_conf(
    key: str, conf_path: str = None,
    default_value: Any = None
) -> Any:
    """ Load a value from a configuration file, or return default if not found or empty.
    """
    workdir_path = os.getenv("PITCHOUNE_WORKDIR")
    workdir_conf_path = None
    if workdir_path:
        workdir_conf_path = os.path.join(workdir_path, ".conf")

    global_conf_path = os.getenv("GLOBAL_CONF_PATH")

    for f in (conf_path, workdir_conf_path, global_conf_path):  # try in order : specific conf file, workdir one or global one
        if f:
            with open(f, "r", encoding="utf8") as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == key:
                            v = v.strip()
                            return v if v else default_value
    print(f"Warning: Key {key} not found in .conf files (default value '{default_value}' applied) !")

    return default_value


def enrich_path(
    path: str|pathlib.Path
) -> str:
    """ Enrich path
    """
    p = str(path)
    p = replace_conf_key_by_conf_value(p)
    if p == None:
        return
    p = replace_home_token_by_home_path(p)
    p = replace_name_token_by_workdir_name(p)
    p = replace_by_module_name_if_only_extension(p)
    p = complete_path_with_workdir(p)
    return p


def Path(
    path: str
):
    """ Enrich path
    """
    return enrich_path(path)


def ConfPath(
    path: str
):
    """ Enrich path
    """
    if path.startswith("conf_path:"):
        raise ValueError("Please remove the prefix 'conf_path:'")
    return enrich_path("conf:" + path)


def ConfInt(
    path: str
):
    """ Enrich path
    """
    return int(enrich_path("conf:" + path))


def ConfFloat(
    path: str
):
    """ Enrich path
    """
    return float(enrich_path("conf:" + path))


def ConfList(
    path: str
):
    """ Enrich path
    """
    return [x.strip() for x in enrich_path("conf:" + path).split(",") if x]


def Conf(
    key: str
):
    """ Enrich path
    """
    return load_from_conf(key)


# others

def get_main_module_name() -> str:
    """ Get the name of the main module (script) without the file extension.
    """
    return os.path.splitext(os.path.basename(sys.modules["__main__"].__file__))[0]


def check_single(
    check: str
) -> bool:
    """ Function used by evaluate_rule function
    """
    if ":" not in check:
        return False
    prefix, key = check.split(":", 1)
    value = load_from_conf(key) if prefix.startswith("conf") else key

    try:
        if prefix in ("path", "conf_path"):
            return Path(value).exists() or (enrich_path(value) and Path(enrich_path(value)).exists())
        elif prefix == "conf":
            return value not in [None, "", []]
        elif prefix == "conf_int":
            return int(value) == float(value)
        elif prefix == "conf_float":
            float(value)
            return True
        elif prefix == "conf_list":
            return isinstance(value, str) and bool([v.strip() for v in value.split(",") if v.strip()])
        else:
            return False
    except Exception:
        return False


def evaluate_rule(
    expr: str
) -> bool:
    """ Function used by requested decorator
    """
    expr = expr.strip()

    tokens = re.split(r'(\(|\)|\&|\|)', expr)
    tokens = [t.strip() for t in tokens if t.strip()]

    def parse(tokens):
        def parse_atom():
            token = tokens.pop(0)
            if token == '(':
                result = parse(tokens)
                if not tokens or tokens.pop(0) != ')':
                    raise ValueError("Parenthèse non fermée")
                return result
            else:
                return lambda: check_single(token)

        def parse_and_or():
            left = parse_atom()
            while tokens and tokens[0] in ('&', '|'):
                op = tokens.pop(0)
                right = parse_atom()
                if op == '&':
                    left = (lambda l=left, r=right: l() and r())
                else:
                    left = (lambda l=left, r=right: l() or r())
            return left

        return parse_and_or()

    return parse(tokens)()
