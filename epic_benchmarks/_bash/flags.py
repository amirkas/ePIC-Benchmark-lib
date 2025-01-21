from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Union, Any, Optional, Callable, Tuple, Hashable, Iterable

class BashExecFlag(BaseModel):
    model_config = ConfigDict(frozen=True)
    flag : str
    value_formatter: Optional[Callable[[Any], Hashable]] = Field(default=None)
    value_validator : Optional[Callable[[Any], bool]] = Field(default=None)
    value_range : Optional[Tuple[float, float]] = Field(default=None)
    enforce_value_as_string : bool = Field(default=True)


    # @field_validator('value_validators', mode='before')
    # def check_validators(cls, value : Any):

    #     if callable(value):
    #         return value
    #     else:
    #         raise ValueError("value_validators must be a callable")

    def validate_value(self, value : Any) -> None:

        if self.value_validator:
            try:
                is_valid = self.value_validator(value)
                if not is_valid:
                    err = f"Value '{value}' is not valid for flag '{self.flag}'"
                    raise ValueError(err)
            except Exception as e:
                raise e
        if self.value_range:
            try:
                in_range = self.value_range[0] <= value <= self.value_range[1]
                if not in_range:
                    err = f"Value '{value}' is not in range for flag '{self.flag}'"
                    raise ValueError(err)
            except ValueError as e:
                raise e

    def bash_format(self, value):

        self.validate_value(value)
        formatted_value = value
        if self.value_formatter:
            formatted_value = self.value_formatter(value)
        if isinstance(formatted_value, str) and len(formatted_value) == 0:
            return self.flag
        if self.enforce_value_as_string:
            return f"{self.flag}='{formatted_value}'"
        return f"{self.flag}={formatted_value}"