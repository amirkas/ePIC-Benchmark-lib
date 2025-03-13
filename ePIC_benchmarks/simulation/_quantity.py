from __future__ import annotations
import numbers
import re
from dataclasses import field, dataclass
from enum import Enum
from typing import Any, ClassVar, Union, Optional, Callable, Self

#Class that stores the relationship between
#a magnitude prefix, and its numerical value
@dataclass(frozen=True)
class MagnitudePrefix:

    character : str
    order : float

    def __repr__(self):
        return self.character

    def magnitude(self):
        return self.order

#Enum of all magnitude prefixes and their associated magnitude coefficients
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

    #Returns the regex pattern for a magnitude prefix
    @classmethod
    def prefix_subpattern(cls):

        return rf"[{"".join(prefix.value.character for prefix in cls)}]"

    #Returns the MagnitudePrefix instance associated with a magnitude prefix character
    @classmethod
    def from_prefix(cls, prefix : str) -> MagnitudePrefix:

        for unit_prefix in cls:
            if prefix == unit_prefix.value.character:
                return unit_prefix.value
        raise ValueError(f"Unknown unit prefix {prefix}")


#Base class for a quantity (Momentum, Theta, Eta, .etc)
@dataclass
class Quantity:

    #Standard unit for a quantity class.
    standard_unit: ClassVar[str] = field(init=False)

    #Delimeter between a quantity instance's value and its unit (often used for bash executables)
    delimiter : ClassVar[str] = field(init=False, default='')

    #Magnitude for an instance of a quantity
    magnitude: Union[float, int] = field(init=True)
    order: Optional[MagnitudePrefix] = field(init=True, default=UnitPrefix.Unity.value)

    #Internally used for comparisons of 2 quantities
    absolute_magnitude : float = field(init=False, default=0.0)

    #Internally used to ensure value is valid for given quantity
    validator : Optional[Callable[[float], bool]] = field(init=False, default=None)

    #Casts a value to a Quantity Class
    #Throws an error if the input value cannot be cast
    @classmethod
    def to_quantity(cls, value : Union[float, str, Self]) -> Self:

        if isinstance(value, type(cls)):
            return value
        elif isinstance(value, numbers.Number):
            return cls(value)
        elif isinstance(value, str):
            return cls.from_string(value)
        else:
            raise ValueError(f"Unsupported type {type(value)}")

    #Returns the regex pattern used to match a string to quantity attributes.
    @classmethod
    def pattern(cls):

        non_decimal_subpattern = "-?[0-9]+"
        decimal_subpattern = ".[0-9]+"
        escaped_unit = re.escape(cls.standard_unit)
        escaped_delimeter = re.escape(cls.delimiter)
        order_subpattern = rf"{UnitPrefix.prefix_subpattern()}?"

        return (
            rf"^({non_decimal_subpattern})({decimal_subpattern})?" 
            rf"({escaped_delimeter})?({order_subpattern})({escaped_unit})?$"
        )
    
    #Returns a quantity class instance from it's string format
    @classmethod
    def from_string(cls, quantity_str : str) -> Self:

        match = re.match(cls.pattern(), quantity_str)
        if not match:
            raise ValueError(f"Could not parse {quantity_str}")
        parsed_magnitude : Union[int, float] = 0
        if match.group(2) is None or len(match.group(2)) == 0:
            parsed_magnitude = int(match.group(1))
        else:
            magnitude_str = match.group(1) + match.group(2)
            parsed_magnitude = float(magnitude_str)
        # parsed_magnitude = int(match.group(1)) if len(match.group(1).isdigit() else float(match.group(1))
        parsed_order = UnitPrefix.from_prefix(match.group(4))
        return cls(parsed_magnitude, parsed_order)

    #Returns the string format for a quantity instance
    def __str__(self) -> str:
        return f"{self.magnitude}{self.delimiter}{self.order}{self.standard_unit}"

    #'Less than' comparator for 2 quantity instances
    def __lt__(self, other : Quantity) -> bool:
        if isinstance(other, numbers.Number):
            return self.absolute_magnitude < other
        self._check_same_type(other)
        return self.absolute_magnitude < other.absolute_magnitude

    #'Greater than' comparator for 2 quantity instances
    def __gt__(self, other : Quantity) -> bool:
        if isinstance(other, numbers.Number):
            return self.absolute_magnitude > other
        self._check_same_type(other)
        return self.absolute_magnitude > other.absolute_magnitude

    #'Equal to' comparator for 2 quantity instances
    def __eq__(self, other : Quantity) -> bool:
        if isinstance(other, numbers.Number):
            return self.absolute_magnitude == other
        self._check_same_type(other)
        return self.absolute_magnitude == other.absolute_magnitude

    #'Less than or equal to' comparator for 2 quantity instances
    def __le__(self, other : Quantity) -> bool:
        return self < other or self == other

    #'Greater than or equal to' comparator for 2 quantity instances
    def __ge__(self, other : Quantity) -> bool:
        return self > other or self == other

    #Returns whether 2 quantity instances have the same quantity type
    def _same_type(self, other : Any) -> bool:
        return isinstance(self, type(other))

    #Throws an error if 2 quantity instances do not have the same quantity type
    def _check_same_type(self, other):

        if not self._same_type(other):
            err = f"Cannot compare {self.__class__.__name__} to {other.__class__.__name__}"
            raise ValueError(err)

    #Post initialization routine
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