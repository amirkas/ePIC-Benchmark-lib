from multiprocessing import Value
import re
from typing import Tuple

def walltime_as_tuple(walltime : str) -> Tuple[int, int, int]:

    pattern = "^(\d[2]):(\d[2]):(\d[2])$"
    match =re.match(pattern, walltime):
    if match is None:
        err = f"invalid format for walltime: '{walltime}'"
        raise ValueError(err)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))