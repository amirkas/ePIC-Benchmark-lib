from typing import Union

from epic_benchmarks.configurations._simulation.types import MomentumUnits, MomentumRange
import re
import numbers
import math

ELECTRON_VOLTS_PATTERN = r'^([mkMGTP]?)(eV)'
MOMENTUM_PATTERN = MomentumUnits.regexPattern()
THETA_PATTERN = rf'^(-?\d+.?\d+)(\*?)(deg)?(ree)?(s)?$'
RADIAN_PATTERN = rf'^(-?\d+.?\d+)(\*?)(rad)?(ian)?(s)?$'

def _validate_momentum_str(momentum : str):

    match = re.match(MOMENTUM_PATTERN, momentum)
    if not match:
        raise ValueError('Invalid momentum')

    magnitude = float(match.group(1))
    if magnitude <= 0:
        raise ValueError('Invalid momentum magnitude. Must be larger than 0.')
    units = match.group(3)
    return f'{magnitude}*{units}'


def _validate_momentum_tuple(magnitude : numbers.Number, units : str):

    momentum_str = f'{magnitude}{units}'
    return _validate_momentum_str(momentum_str)


def _validate_angle_deg(angle : Union[numbers.Number, str]):

    if isinstance(angle, str):
        match = re.match(THETA_PATTERN, angle)
        if not match:
            raise ValueError('Invalid angle')
        angle = float(match.group(1))

    if angle < 0.0 or angle > 360.0:
        raise ValueError('Invalid angle. Angle must be between 0 and 360. Got {angle}')
    return f'{float(angle)}*degree'


def _validate_angle_rad(angle : Union[numbers.Number, str]):

    if isinstance(angle, str):
        match = re.match(RADIAN_PATTERN, angle)
        if not match:
            raise ValueError('Invalid format')
        angle = math.degrees(float(match.group(1)))

    return _validate_angle_deg(angle)


def _validate_eta(angle : Union[numbers.Number, str]):

    return angle




















#Validate configuration values
def validate_momentum(momentum) -> bool:
    if not isinstance(momentum, numbers.Number) and not isinstance(momentum, str):
        raise Exception("Momentum must be a string or a number")

    if isinstance(momentum, str):
        match = re.match(MOMENTUM_PATTERN, momentum)
        if not match:
            raise AttributeError("Momentum does not have a valid format.")
        if match and not MomentumRange.in_range(match.group(1)):
            raise AttributeError(f"Momentum is not in range of allowed momenta. Allowed range is {MomentumRange}")
    return True

def format_momentum(momentum):

    if isinstance(momentum, str):
        match = re.match(MOMENTUM_PATTERN, momentum)
        assert match
        momentum_value = match.group(1)
        units = match.group(3)
        if len(units) == 0:
            units = "MeV"

    else:
        momentum_value = momentum
        units = "MeV" #TODO: Placeholder, add behaviour for input units
    return f"{momentum_value}*{units}"