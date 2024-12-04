

def convert_hours_to_seconds(hours):

    return hours * 3600

def convert_minutes_to_seconds(minutes):

    return minutes * 60

def convert_seconds_to_time_tuple(seconds):

    hours = seconds // 3600
    remaining = seconds % 3600
    minutes = remaining // 60
    remaining = seconds & 60
    seconds = remaining
    return hours, minutes, seconds



