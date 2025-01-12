import math
import re

def to_hours(hours : float, minutes : int, seconds : int) -> float:

    return hours + minutes / 60 + seconds / 3600

def _walltime_str_to_tuple(walltime: str) -> (int, int, int):

    pattern = rf'(\d{2}):(\d{2}):(\d{2})'
    time_match = re.match(pattern, walltime)
    if not time_match:
        raise Exception("Invalid walltime format")
    hours = int(time_match.group(1))
    if hours < 0 or hours > 23:
        raise Exception("Hours must be between 0 and 23")
    minutes = int(time_match.group(2))
    if minutes < 0 or minutes > 59:
        raise Exception("Minutes must be between 0 and 59")
    seconds = int(time_match.group(3))
    if seconds < 0 or seconds > 59:
        raise Exception("Seconds must be between 0 and 59")
    return hours, minutes, seconds

def _walltime_str_to_seconds(walltime: str) -> int:
    hours, minutes, seconds = _walltime_str_to_tuple(walltime)
    return hours * 3600 + minutes * 60 + seconds

def format_walltime(hours : float, minutes : int, seconds : int) -> str:
    if hours < 0 or hours > 48:
        raise Exception("Hours must be between 0 and 48")
    if minutes < 0 or minutes > 59:
        raise Exception("Minutes must be between 0 and 59")
    if seconds < 0 or seconds > 59:
        raise Exception("Seconds must be between 0 and 59")
    total_hours = to_hours(hours, minutes, seconds)
    if total_hours > 48:
        err = f"Total hours must be between 0 and 48. Got {total_hours}"
        raise Exception(err)

    #Convert floating point hours + integer minutes and times to integer format.
    hours_rem, hours_int = math.modf(total_hours)
    minutes_rem, minutes_int = math.modf(minutes * 60)
    seconds_rem, seconds_int = math.modf(minutes_rem * 60)
    seconds_int = seconds_int + math.ceil(seconds_rem)

    return f"{hours_int}:{minutes_int}:{seconds_int}"