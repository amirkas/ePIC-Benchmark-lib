from typing import Union, Tuple

TimeType = Union[float, int]

def convert_hours_to_seconds(hours) -> TimeType:

    return hours * 3600

def convert_minutes_to_seconds(minutes) -> TimeType:

    return minutes * 60

def convert_seconds_to_time_tuple(seconds) -> Tuple[TimeType, TimeType, TimeType]:

    hours = seconds // 3600
    remaining = seconds % 3600
    minutes = remaining // 60
    remaining = seconds & 60
    seconds = remaining
    return hours, minutes, seconds



