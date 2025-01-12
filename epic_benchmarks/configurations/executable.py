import numbers

from pydantic import BaseModel, field_validator, Field, ConfigDict
from dataclasses import dataclass, fields, field, is_dataclass
from typing import Dict, Union, Any, Optional, Callable, Tuple, Hashable, Iterable, Set, List

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings








class Executable(BaseModel):

    executable_name : str = Field(..., init=False)


    def __str__(self):

        command_str = f"{self.executable_name}"

        all_fields = self.model_fields
        for field_name, field_info in all_fields.items():

            if field_name == "executable_name":
                continue

            field_val = getattr(self, field_name, None)

            if "flag_delimiter" in field_info.json_schema_extra.keys():
                delimiter = str(field_info.json_schema_extra["flag_delimiter"])
            else:
                delimiter = "--"

            if isinstance(field_val, bool) and "cli_implicit" in field_info.json_schema_extra.keys():
                if field_info.json_schema_extra["cli_implicit"] and field_val:
                    command_str += f" {delimiter}{field_name}={field_val}"


            flag_substr = f" {field_name}"
            if "cli_implicit" in field_info.json_schema_extra.keys() and field_info.json_schema_extra["cli_implicit"]:
                command_str = command_str + flag_substr

        return ""












class BashExecFlag(BaseModel):
    model_config = ConfigDict(frozen=True)
    flag : str
    value_formatter: Optional[Callable[[Any], Hashable]] = Field(default=None)
    value_validators : Optional[Union[Callable[[Any], bool], frozenset[Callable[[Any], bool]]]] = Field(default=None)
    value_range : Optional[Tuple[float, float]] = Field(default=None)
    enforce_value_as_string : bool = Field(default=True)


    @field_validator('value_validators', mode='before')
    def check_validators(cls, value : Any):

        if callable(value):
            return frozenset([value])
        elif isinstance(value, Iterable):
            return frozenset(value)
        else:
            raise ValueError("value_validators must be a callable or a iterable of callables")

    def validate_value(self, value : Any) -> None:

        if self.value_validators:
            for validator in self.value_validators:
                try:
                    is_valid = validator(value)
                    if not is_valid:
                        raise ValueError("Value is not valid")
                except Exception as e:
                    raise e
        if self.value_range:
            try:
                in_range = self.value_range[0] <= value <= self.value_range[1]
                if not in_range:
                    raise ValueError("Value is not in range")
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







# #Base class for representing a Bash Executable Flag
# @dataclass(frozen=True)
# class BashExecFlag:
#
#     flag : str
#     value_types : Union[Type, list[Type], None] = field(hash=False)
#
#     value_is_numeric : bool = False
#     value_is_alphabetic : bool = False
#     value_is_file : bool = False
#     file_exists : bool = False
#     include_bool : bool = True
#
#     value_range : Optional[Range] = field(default=None, hash=False)
#     value_prefix : Optional[str] = field(default="", hash=True)
#     value_suffix : Optional[str] = field(default="", hash=True)
#
#     def __post_init__(self):
#
#         #Validate that value types are either int, float, str, or None
#         self._validate_flag()
#
#     def bash_format(self, value=None) -> str:
#         #Validate the value
#         try:
#             self._validate_value(value)
#         except Exception as e:
#             raise e
#
#         #Edge case 1: If value is none just return the flag
#         if value is None:
#             return self.flag
#
#         #Edge case 2: If flag has boolean value but does not include it, just return the flag
#         if isinstance(value, bool) and not self.include_bool:
#             return self.flag
#
#         #Edge case 3: If flag is empty, do not append '='.
#         if len(self.flag) == 0:
#             flag_str = ''
#         else:
#             flag_str = f'{self.flag}='
#
#         # Format value with provided prefix and suffix
#         complete_val = f'{self.value_prefix}{value}{self.value_suffix}'
#
#         bash_str = ""
#         if type(value) == int or type(value) == float:
#             bash_str = f'{flag_str}{complete_val}'
#         elif type(value) == str:
#             bash_str = f'{flag_str}"{complete_val}"'
#
#         return bash_str
#
#
#     def _validate_flag(self):
#         #Convert single value type to list to reduce code repetition
#         flag_types = self.value_types
#         if not isinstance(self.value_types, list):
#             flag_types = [self.value_types]
#
#         for flag_type in flag_types:
#             if flag_type not in VALID_FLAG_VALUE_TYPES:
#                 raise AttributeError(f"Flag Value Type must be one of '[{", ".join(map(str, VALID_FLAG_VALUE_TYPES))}]'. Got {flag_type}")
#
#         #Additional check if user specified at least a (flag of length > 0) and / or (a value that is not None)
#         if len(self.flag) == 0 and None in flag_types:
#             raise AttributeError(f"Cannot have a Zero length flag with a None type value")
#
#         #Additional check to ensure user Flag is enforced to be (numeric or alphabetic) or (numeric or file), not both.
#         if self.value_is_numeric and self.value_is_alphabetic:
#             raise AttributeError(f"Value cannot be both numeric and alphabetic")
#
#         if self.value_is_numeric and self.value_is_file:
#             raise AttributeError(f"Value cannot be both numeric and a file path")
#
#         #Additional check to see if value_is_file is True if file_exists is specified as True
#         if self.file_exists and not self.value_is_file:
#             raise AttributeError(f"Value")
#
#     def _validate_value(self, value=None):
#
#         try:
#             self._validate_value_type(value)
#             self._validate_numeric(value)
#             self._validate_in_range(value)
#             self._validate_alphabetic(value)
#             self._validate_file_path(value)
#             self._validate_file_exists(value)
#         except Exception as e:
#             raise e
#
#     def _validate_value_type(self, value):
#         flag_types = self.value_types
#         if not isinstance(self.value_types, list):
#             flag_types = [self.value_types]
#         valid_type_found = False
#         for flag_type in flag_types:
#             if flag_type and isinstance(value, flag_type):
#                 valid_type_found = True
#         if not valid_type_found:
#             err = f"Value type must be one of [{", ".join(map(str, flag_types))}]. Got {type(value)}" # type: ignore
#             raise ValueError(err)
#
#
#     #Check if value must be numeric
#     def _validate_numeric(self, value):
#         if self.value_is_numeric and not isinstance(value, numbers.Number):
#             raise Exception(f"value must be convertible to a number. Got {value}")
#
#     def _validate_alphabetic(self, value):
#         if self.value_is_alphabetic and (not isinstance(value, str) or not value.isalpha()):
#             raise Exception(f"value must be a non numeric string. Got {value}")
#
#     def _validate_file_path(self, value):
#         if self.value_is_file:
#             try:
#                 os.path.normpath(value)
#             except Exception as e:
#                 raise e
#
#     def _validate_in_range(self, value):
#         if self.value_range:
#             try:
#                 self.value_range.validate(value)
#             except Exception as e:
#                 raise e
#
#
#     def _validate_file_exists(self, value):
#         if self.file_exists:
#             try:
#                 exists = os.path.exists(value)
#                 if not exists:
#                     raise AttributeError(f"File at '{value}' does not exist")
#             except Exception as e:
#                 raise e

#Base class for representing a bash executable
@dataclass
class BashExecutable:

    executable : str = field(default="", init=True)
    _flag_container: Optional[Any] = field(default=None, init=False)
    flag_value_map : Dict[BashExecFlag, Any] = field(default_factory=dict, init=False)

    #Lists all required flags that must be set to execute a bash command.
    #A requirement may also be a set of flags of which one must be set.
    required_flags : Set[Union[BashExecFlag, Set[BashExecFlag]]] = field(default_factory=set, init=False)
    last_flag : BashExecFlag = field(default=None, init=False)


    def flags(self) -> List[BashExecFlag]:
        _flags = []
        for _field in fields(self._flag_container):
            attr = getattr(self._flag_container, _field.name)
            if isinstance(attr, BashExecFlag):
                _flags.append(attr)
        return _flags

    def set_flag_val(self, flag : BashExecFlag, value : Any) -> None:
        executable_flags = self.flags()
        if flag not in executable_flags:
            raise AttributeError(f"Flag '{flag.flag}' is not a flag for this executable. The following flags are available:") #TODO: Add string representation
        self.flag_value_map[flag] = value

    def set_all_flags_vals(self, flag_value_dictionary : Dict[str, Any]):
        self.flag_value_map = flag_value_dictionary

    def generate_cmd(self) -> str:

        self._check_required_flags_set()

        executable_string = self.executable + ' '
        for flag, value in self.flag_value_map.items():
            #Do not add specified last flag until the end
            if flag is not self.last_flag:
                executable_string += flag.bash_format(value) + ' '
        if self.last_flag:
            last_val = self.flag_value_map.items()
            executable_string += self.last_flag.bash_format(last_val)
        return executable_string

    def _check_required_flags_set(self) -> Union[Exception, None]:
        set_flags = self.flag_value_map.keys()
        required_flags_to_set = []
        for required_flag in self.required_flags:
            if isinstance(required_flag, BashExecFlag) and required_flag not in set_flags:
                required_flags_to_set.append(required_flag)
            elif isinstance(required_flag, set) and any(r_flag in set_flags for r_flag in required_flag):
                required_options = list(required_flag)
                required_flags_to_set.append(required_options)
            else:
                raise ValueError("Required flag must be a BashExecFlag or a set of BashExecFlags")

        if len(required_flags_to_set) > 0:
            err = f"Cannot generate command since not all required flags are set. Remaining flags to be set: {required_flags_to_set}"
            raise ValueError(err)


    def __post_init__(self):

        if self._flag_container is not None and not is_dataclass(self._flag_container):
            raise Exception("Provided flag container must be a dataclass.")

