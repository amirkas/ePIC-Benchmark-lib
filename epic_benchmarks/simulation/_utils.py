
from enum import Enum
from typing import Any, Type

from pydantic import ValidationError

def validate_enum(value : Any, enum_type : Type):

    assert(issubclass(enum_type, Enum))
    if isinstance(value, str):
        #Check if value is one of the enum's members' names or values.
        for member in enum_type:
            assert(isinstance(member, Enum))
            if value == member.name:
                return member
            elif value == member.value:
                return member
        err = f"Could not find member of enum '{enum_type.__name__}' with name or value '{value}'"
        raise ValueError(err)
    if isinstance(value, Enum) and value in enum_type:
        return value
    else:
        err = f"Value must be an enum or string. Got type '{type(value)}'"
        raise ValueError(err)

