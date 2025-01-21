import os
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel

from epic_benchmarks._file.supported import SUPPORTED_FILE_EXTENSIONS, FILE_EXTENSION_DUMP_MAP, FILE_EXTENSION_LOAD_MAP
from epic_benchmarks._file.types import PathType

def final_filepath(file_path : PathType, file_extension : Optional[str]) -> Path:

    if isinstance(file_extension, str):
        file_path = os.path.join(file_path, file_extension)
    return file_path

def validate_file_support(file_path : PathType) -> None:

    file_extension = get_file_extension(file_path)
    if file_extension not in SUPPORTED_FILE_EXTENSIONS:
        err = (f"File extension '{file_extension}' not supported yet. "
               f"Make a request to support it by submitting an issue to"
               f"the epicbenchmarks github.")
        raise Exception(err)


def get_file_extension(file_path : PathType) -> str:

    _, file_extension = os.path.splitext(file_path)
    return file_extension

def save_serialized_config(serialized_config : Any, file_path : PathType, file_extension=None, overwrite=False) -> None:

    file_path = final_filepath(file_path, file_extension)
    validate_file_support(file_path)
    file_extension = get_file_extension(file_path)

    write_type = "w" if overwrite else "a"
    with open(file_path, write_type) as f:

        dump_func = FILE_EXTENSION_DUMP_MAP[file_extension]
        dump_func(serialized_config, f)

def save_raw_config(raw_config : BaseModel, file_path : PathType, file_extension=None, overwrite=False) -> None:

    serialized_config = raw_config.model_dump()
    save_serialized_config(serialized_config, file_path, file_extension, overwrite)


def load_from_file(file_path : PathType, file_extension=None) -> Any:

    file_path = final_filepath(file_path, file_extension)
    validate_file_support(file_path)
    file_extension = get_file_extension(file_path)
    with open(file_path, 'r') as f:

        load_func = FILE_EXTENSION_LOAD_MAP[file_extension]
        return load_func(f)