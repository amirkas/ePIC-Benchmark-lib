from typing import Union
from pathlib import Path

PathType = Union[str, Path]

def serialize_path_type(path : PathType) -> str:

    if isinstance(path, Path):
        return str(path)
    else:
        return path