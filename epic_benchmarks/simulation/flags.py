import numbers
from enum import Enum
from typing import Any, Type
import os
from pathlib import Path
from epic_benchmarks._bash.flags import BashExecFlag
from epic_benchmarks.simulation.types import Particle, GunDistribution, Momentum, Angle, Eta, Quantity

NPSIM_METADATA_KEY = "npsim"
EICRECON_METADATA_KEY = "eicrecon"

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
        print(resolved_path)
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

    if isinstance(value, Momentum):
        return True
    try:
        As_momentum = Momentum.to_quantity(value)
        return True
    except:
        return False

def is_distribution_value(value : any) -> bool:

    #TODO: Update once new distributions are supported
    return is_angle(value) or is_eta(value)

def is_angle(value : any) -> bool:
    if isinstance(value, Angle):
        return True
    try:
        As_momentum = Angle.to_quantity(value)
        return True
    except:
        return False

def is_eta(value : any) -> bool:
    if isinstance(value, Eta):
        return True
    try:
        As_momentum = Eta.to_quantity(value)
        return True
    except:
        return False


class NpsimFlag(Enum):
    CompactFile: BashExecFlag = BashExecFlag(
        flag="--compactFile",
        # value_validators=is_file_path_readable
    )
    NumEvents: BashExecFlag = BashExecFlag(
        flag="--numberOfEvents", value_validators=is_integer,
        value_formatter=lambda x: int(x),
        enforce_value_as_string=False
    )
    EnableGun: BashExecFlag = BashExecFlag(
        flag="--enableGun",
        value_formatter=lambda x: ""
    )
    GunDistribution: BashExecFlag = BashExecFlag(
        flag="--gun.distribution",
        # value_validator=is_gun_distribution,
        value_formatter=lambda x : str(x)
    )
    GunParticle: BashExecFlag = BashExecFlag(
        flag="--gun.particle",
        # value_validator=is_particle,
        value_formatter=lambda x : str(x)
    )
    GunMomentumMax: BashExecFlag = BashExecFlag(
        flag="--gun.momentumMax",
        # value_validator=is_momentum,
        value_formatter=lambda x : str(x)
    )
    GunMomentumMin: BashExecFlag = BashExecFlag(
        flag="--gun.momentumMin",
        # value_validator=is_momentum,
        value_formatter=lambda x : str(x)
    )
    GunThetaMax: BashExecFlag = BashExecFlag(
        flag="--gun.thetaMax",
        # value_validator=is_angle,
        value_formatter=lambda x : str(x)
    )
    GunThetaMin: BashExecFlag = BashExecFlag(
        flag="--gun.thetaMin",
        # value_validator=is_angle,
        value_formatter=lambda x : str(x)
    )
    GunEtaMax: BashExecFlag = BashExecFlag(
        flag="--gun.etaMax",
        # value_validator=is_eta,
        value_formatter=lambda x : str(x)
    )
    GunEtaMin: BashExecFlag = BashExecFlag(
        flag="--gun.etaMin",
        # value_validator=is_eta,
        value_formatter=lambda x : str(x)
    )
    GunMultiplicity: BashExecFlag = BashExecFlag(
        flag="--gun.multiplicity",
        # value_validator=is_numeric,
        value_formatter=lambda x : float(x)
    )
    OutputFile: BashExecFlag = BashExecFlag(
        flag="--OutputFile",
        # value_validators=is_file_path_writeable
    )

class EicreconFlag(Enum):
    CompactFile: BashExecFlag = BashExecFlag(
        flag="-Pdd4hep:xml_files",
        # value_validators=is_file_path_readable
    )
    NumEvents: BashExecFlag = BashExecFlag(
        flag="-Pjana:nevents",
        # value_validator=is_integer,
        value_formatter=lambda x: int(x),
        enforce_value_as_string=False
    )
    NumThreads: BashExecFlag = BashExecFlag(
        flag="-Pnthreads",
        # value_validator=is_integer,
        value_formatter=lambda x: int(x),
        enforce_value_as_string=False
    )
    OutputFile: BashExecFlag = BashExecFlag(
        flag="-Ppodio:output_file",
        # value_validators=is_file_path_writeable
    )
    InputFile: BashExecFlag = BashExecFlag(
        flag="",
        # value_validators=is_file_path_writeable
    )