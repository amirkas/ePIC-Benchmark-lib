import numbers
from enum import Enum
from typing import Any, Type
import os
from pathlib import Path
from epic_benchmarks.configurations.simulation_types import Particle, GunDistribution, Momentum, Angle, Eta, Quantity


def is_alphabetic(value : Any) -> bool:

    if not isinstance(value, str):
        return False
    return value.isalpha()


def is_numeric(value : Any) -> bool:

    if isinstance(value, numbers.Number):
        return True
    elif isinstance(value, str):
        return value.isdigit() or value.isdecimal()
    else:
        return False

def is_integer(value : Any) -> bool:

    if not is_numeric(value):
        return False
    return str(int(value)) == str(value)


def is_path_accessible(value : Any, access_type : Any) -> bool:

    try:
        resolved_path = Path(value).resolve()
        if resolved_path.exists():
            return os.access(resolved_path, access_type)
        else:
            return is_directory_path_writeable(resolved_path.parent)
    except:
        return False

def is_directory_path_writeable(value : Any) -> bool:

    resolved_path = Path(value).resolve()
    return is_path_accessible(value, os.W_OK) and resolved_path.is_dir()


def is_file_path_writeable(value : any) -> bool:
    resolved_path = Path(value).resolve()
    return is_path_accessible(value, os.W_OK) and resolved_path.is_file()

def is_directory_path_readable(value : any) -> bool:
    resolved_path = Path(value).resolve()
    return is_path_accessible(value, os.R_OK) and resolved_path.is_dir()

def is_file_path_readable(value : any) -> bool:
    resolved_path = Path(value).resolve()
    return is_path_accessible(value, os.R_OK) and resolved_path.is_file()


def path_exists(value : Any) -> bool:

    try:
        resolved_path = Path(value).resolve()
        return resolved_path.exists()
    except:
        return False

def directory_exists(value : Any) -> bool:

    try:
        if not path_exists(value):
            return False
        resolved_path = Path(value).resolve()
        return resolved_path.is_dir()
    except:
        return False

def file_exists(value : any) -> bool:

    try:
        if not path_exists(value):
            return False
        resolved_path = Path(value).resolve()
        return resolved_path.is_file()
    except:
        return False


def is_enum(value : any, enum : Enum) -> bool:

    if isinstance(value, enum):
        return True
    for e in enum:
        if value == e.value:
            return True
    return False

def is_quantity(value : any, quantity : Type[Quantity]) -> bool:

    if isinstance(value, quantity):
        return True
    elif isinstance(value, numbers.Number):
        try:
            q = quantity(value)
            return True
        except:
            return False
    elif isinstance(value, str):
        try:
            q = quantity.from_string(value)
            return True
        except:
            return False
    else:
        return False


def is_particle(value : any) -> bool:

    return is_enum(value, Particle)

def is_gun_distribution(value : any) -> bool:

    return is_enum(value, GunDistribution)

def is_momentum(value : any) -> bool:

    return is_quantity(value, Momentum)

def is_distribution_value(value : any) -> bool:

    #TODO: Update once new distributions are supported
    return is_angle(value) or is_eta(value)

def is_angle(value : any) -> bool:
    return is_enum(value, Angle)

def is_eta(value : any) -> bool:
    return is_enum(value, Eta)



