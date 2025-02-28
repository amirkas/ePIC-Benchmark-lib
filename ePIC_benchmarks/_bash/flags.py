from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import ClassVar, Literal, Sequence, Any, Optional, TypeVar, Generic

T = TypeVar('T')

@dataclass
class BashFlag(Generic[T]):

    value : Optional[T] = field(default=None)
    flag : ClassVar[Literal['']] = ''
    coerce_to_str : ClassVar[bool] = False
    exclude_bool_arg : ClassVar[bool] = True
    use_enum_val : ClassVar[bool] = False

    def __repr__(self) -> str:
        return self.__class__.flag_string(self.value)
        
    @classmethod
    def flag_string(cls, value):

        val = value
        if val is None:
            return ""
        if isinstance(val, bool) and cls.exclude_bool_arg:
            return cls.flag if val else ""
        
        if isinstance(val, Enum):
            if cls.use_enum_val:
                val = val.value
            else:
                val = val.name
        if not isinstance(val, str) and not cls.coerce_to_str:
            if len(cls.flag) == 0:
                return str(val)
            return f"{cls.flag}={val}"
        else:
            if len(cls.flag) == 0:
                return f"'{val}'"
            return f"{cls.flag}='{val}'"


class BashCommand(BaseModel):

    model_config = ConfigDict(
        extra='ignore', validate_default=True,
        validate_assignment=True, arbitrary_types_allowed=True
    )

    executable_command : ClassVar[str]
    extra : Optional[Sequence[BashFlag[Any]]] = Field(default=None)

    def generate_command(self) -> str:

        command = f"{self.executable_command}"
        if self.extra is not None:
            for flag in self.extra:
                command += " " + str(flag)
        dumped_fields = self.model_dump()
        for field_name in self.model_fields_set:
            field_val = dumped_fields[field_name]
            command += " " + str(field_val)
        return command

