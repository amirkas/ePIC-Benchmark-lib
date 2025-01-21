from enum import Enum
from typing import Union

from dataclasses import dataclass
from epic_benchmarks.simulation._quantity import Quantity

@dataclass
class Momentum(Quantity):

    standard_unit = "eV"

@dataclass
class Angle(Quantity):

    standard_unit = "degrees"
    validator = lambda x: 0 <= x <= 360

@dataclass
class Eta(Quantity):

    standard_unit = ""

DistributionLimitType = Union[Angle, Eta]

class Particle(Enum):
    PionNeutral = "pi"
    PionPlus = "pi+"
    PionNeg = "pi-"
    #TODO: Add all particles

class GunDistribution(Enum):
    
    def __new__(cls, string_value : str, limit_type : DistributionLimitType):
        
        new_obj = object.__new__(cls)
        new_obj._value_ = string_value
        new_obj.limit_type = limit_type
        return new_obj

    Uniform = ("uniform", Angle)
    Eta = ("eta", Eta)
    #TODO: Add other distributions and assess their input requirements


