import os
from pathlib import Path
import re
import shutil
import sys
import typing
import zipfile
import time
import subprocess
import platform

from rapidfuzz.distance import Levenshtein
import polars as pl


# polars functions

def check_duplicates(df: pl.DataFrame, *id_cols: str) -> None:
    """Throw an error if duplicates are found in the dataframe."""
    duplicates = df.group_by(id_cols).count().filter(pl.col("count") > 1)
    if len(duplicates) > 0:
        raise ValueError(f"Des doublons ont été trouvés :\n{duplicates}")


def to_path(value: Path|str) -> Path:
    """Cast a string to a Path object if it's a string."""
    return value if isinstance(value, Path) else Path(value)


# files functions

def replace_in_file(filepath: Path, repl_mapping: dict[str, str], file_suffix: str = "~") -> Path:
    """Replace expressions in a file and save the result to a new file."""
    with open(str(filepath), "r", encoding="utf8") as f:
        data = f.read()
    for text_to_replace, replaced_by in repl_mapping.items():
        new_data = data.replace(text_to_replace, replaced_by)
    new_filepath = filepath.with_name(f"{filepath.stem}~{filepath.suffix}") if file_suffix else filepath
    with open(str(new_filepath), "w", encoding="utf8") as f:
        f.write(new_data)
    return new_filepath


def unzip(zip_filepath: Path|str) -> str:
    """Unzips a .zip file and returns the path to the extracted folder."""
    destination_folder = os.path.splitext(zip_filepath)[0]  # Remove the .zip extension
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:  # Extract the zip file into the destination folder
        zip_ref.extractall(destination_folder)
        return destination_folder


def watch_file(filepath: str):
    """Watch a file for changes and return when it is modified."""
    last_modif = os.path.getmtime(filepath)
    while True:
        time.sleep(2)  # Attente avant de vérifier à nouveau
        new_modif = os.path.getmtime(filepath)
        if new_modif != last_modif:
            break


def open_file(file_path):
    """Opens the given file with its default editor."""
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", file_path])
    else:  # Linux
        subprocess.run(["xdg-open", file_path])


# string functions

def replace_in_expr(expr: str, repl_mapping: dict[str, str]) -> str:
    """Replace expressions in another expression."""
    if not new_part in expr:
        for old_part, new_part in repl_mapping.items():
            expr = expr.replace(old_part, new_part)
        return expr
    return expr


def anonymize(text: str) -> str:
    """Anonymize sensitive information in a text by replacing it with asterisks."""
    PHONE_REGEX = r"\+?\d{1,4}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}"
    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    if text is None:
        return None
    text = re.sub(EMAIL_REGEX, "**********", text)
    text = re.sub(PHONE_REGEX, "**********", text)
    return text


def percentage_difference(str1: str, str2: str) -> float:
    """Calculate the percentage difference between two strings using Levenshtein distance."""
    max_len = max(len(str1), len(str2))
    if max_len == 0:
        return 0  # Avoid division by zero
    return (Levenshtein.distance(str1, str2) / max_len) * 100


# Path functions

def extract_subfolder_contents(parent_folder: str) -> None:
    """Moves contents from a uniquely named subfolder to `parent_folder` and deletes the subfolder if empty."""
    subfolders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]  # Get subfolders inside parent_folder
    if len(subfolders) == 1 and subfolders[0] == os.path.basename(parent_folder):  # Ensure there is **only one** subfolder and its name matches `parent_folder`
        subfolder_path = os.path.join(parent_folder, subfolders[0])
        for item in os.listdir(subfolder_path):  # Move all contents to parent folder
            shutil.move(os.path.join(subfolder_path, item), parent_folder)
        os.rmdir(subfolder_path)  # Remove the now-empty subfolder


def iter_all_files(root_folder: Path|str) -> typing.Generator[Path, None, None]:
    """Recursively yields file paths inside subdirectories of `root_folder`."""
    for folder, _, files in os.walk(root_folder):
        for file in files:
            yield Path(os.path.join(folder, file))  # Yield file paths one by one


def is_only_extension(path) -> bool:
    """Check if the path has only one component and is a file extension."""
    return len(path) > 1 and path[0] == '.' and "/" not in path


def change_suffix(filepath: str, new_suffix: str):
    """Change the file extension while preserving the original name."""
    filepath = Path(filepath)
    filepath = filepath.with_suffix(new_suffix)
    return filepath


def complete_path_with_workdir(filepath: str|Path) -> Path:
    """Complete the file path with the pitchoune working directory."""
    workdir = os.getenv("PITCHOUNE_WORKDIR")
    return workdir / to_path(filepath) if workdir else to_path(filepath)


# other functions


def get_main_module_name() -> str:
    """Get the name of the main module (script) without the file extension."""
    return os.path.splitext(os.path.basename(sys.modules["__main__"].__file__))[0]

