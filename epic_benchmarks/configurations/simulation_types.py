from __future__ import annotations
import numbers
import re
from dataclasses import field, dataclass
from enum import Enum
from typing import List, Union, Optional, Callable

class Particle(Enum):
    PionNeutral = "pi"
    PionPlus = "pi+"
    PionNeg = "pi-"
    #TODO: Add all particles

class GunDistribution(Enum):
    Uniform = "uniform"
    Eta = "eta"
    #TODO: Add other distributions and assess their input requirements

@dataclass(frozen=True)
class MagnitudePrefix:

    character : str
    order : float

    def __repr__(self):
        return self.character

    def magnitude(self):
        return self.order

class UnitPrefix(Enum):

    Yocto : MagnitudePrefix = MagnitudePrefix("y", 10 ** (-24))
    Zepto : MagnitudePrefix = MagnitudePrefix("z", 10 ** (-21))
    Atto : MagnitudePrefix = MagnitudePrefix("a", 10 ** (-18))
    Femto : MagnitudePrefix = MagnitudePrefix("f", 10 ** (-15))
    Pico : MagnitudePrefix = MagnitudePrefix("p", 10 ** (-12))
    Nano : MagnitudePrefix = MagnitudePrefix("n", 10 ** (-9))
    Micro : MagnitudePrefix = MagnitudePrefix("u", 10 ** (-6))
    Milli : MagnitudePrefix = MagnitudePrefix("m", 10 ** (-3))
    Unity : MagnitudePrefix = MagnitudePrefix("", 1)
    Kilo : MagnitudePrefix = MagnitudePrefix("k", 10 ** 3)
    Mega : MagnitudePrefix = MagnitudePrefix("M", 10 ** 6)
    Giga : MagnitudePrefix = MagnitudePrefix("G", 10 ** 9)
    Tera : MagnitudePrefix = MagnitudePrefix("T", 10 ** 12)
    Peta : MagnitudePrefix = MagnitudePrefix("P", 10 ** 15)
    Exa : MagnitudePrefix = MagnitudePrefix("E", 10 ** 18)


    @classmethod
    def prefix_subpattern(cls):

        return rf"[{"".join(prefix.value.character for prefix in cls)}]"

    @classmethod
    def from_prefix(cls, prefix : str) -> MagnitudePrefix:

        for unit_prefix in cls:
            if prefix == unit_prefix.value.character:
                return unit_prefix.value
        raise ValueError(f"Unknown unit prefix {prefix}")



@dataclass
class Quantity:

    standard_unit: str = field(init=False)
    magnitude: float = field(init=True)
    order: Optional[MagnitudePrefix] = field(init=True, default=UnitPrefix.Unity.value)

    #Internally used for comparisons of 2 quantities
    absolute_magnitude : float = field(init=False, default=None)

    #Internally used to ensure value is valid for given quantity
    validator : Optional[Callable[[float], bool]] = field(init=False, default=None)

    @classmethod
    def to_quantity(cls, value : Union[float, str, Quantity]) -> Quantity:

        if isinstance(value, type(cls)):
            return value
        elif isinstance(value, numbers.Number):
            return cls(value)
        elif isinstance(value, str):
            return cls.from_string(value)
        else:
            raise ValueError(f"Unsupported type {type(value)}")

    @classmethod
    def pattern(cls):

        magnitude_subpattern = rf"-?\d+.?\d+"
        order_subpattern = rf"{UnitPrefix.prefix_subpattern()}?"
        unit_subpattern = cls.standard_unit

        return rf"^({magnitude_subpattern})\*?({order_subpattern})({unit_subpattern})?$"

    @classmethod
    def from_string(cls, quantity_str : str):

        match = re.match(cls.pattern(), quantity_str)
        if not match:
            raise ValueError(f"Could not parse {quantity_str}")
        parsed_magnitude = int(match.group(1)) if match.group(1).isdigit() else float(match.group(1))
        parsed_order = UnitPrefix.from_prefix(match.group(2))
        return cls(parsed_magnitude, parsed_order)

    def __str__(self):
        return f"{self.magnitude}*{self.order}{self.standard_unit}"

    def __lt__(self, other):
        if isinstance(other, numbers.Number):
            return self.absolute_magnitude < other
        self._check_same_type(other)
        return self.absolute_magnitude < other.absolute_magnitude

    def __gt__(self, other):
        if isinstance(other, numbers.Number):
            return self.absolute_magnitude > other
        self._check_same_type(other)
        return self.absolute_magnitude > other.absolute_magnitude

    def __le__(self, other):
        if isinstance(other, numbers.Number):
            return self.absolute_magnitude <= other
        self._check_same_type(other)
        return self.absolute_magnitude <= other.absolute_magnitude

    def __ge__(self, other):
        if isinstance(other, numbers.Number):
            return self.absolute_magnitude >= other
        self._check_same_type(other)
        return self.absolute_magnitude >= other.absolute_magnitude

    def __eq__(self, other):
        if isinstance(other, numbers.Number):
            return self.absolute_magnitude == other
        self._check_same_type(other)
        return self.absolute_magnitude == other.absolute_magnitude

    def _same_type(self, other):

        return isinstance(self, type(other))

    def _check_same_type(self, other):

        if not self._same_type(other):
            err = f"Cannot compare {self.__class__.__name__} to {other.__class__.__name__}"
            raise ValueError(err)

    def __post_init__(self):

        #Convert magnitude to absolute magnitude using given order.
        order_magnitude = 1
        if self.order:
            order_magnitude = self.order.magnitude()

        self.absolute_magnitude = self.magnitude * order_magnitude

        #Validate absolute magnitude if validator is defined
        if self.__class__.validator and not self.__class__.validator(self.absolute_magnitude):
            err = f"The given value '{self.magnitude}{self.order}{self.standard_unit}' is not valid"
            raise ValueError(err)

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
