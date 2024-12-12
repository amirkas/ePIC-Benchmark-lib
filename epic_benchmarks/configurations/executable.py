import numbers
from epic_benchmarks.configurations.ranges import Range
from dataclasses import dataclass, fields, field, is_dataclass
from typing import Type, Dict, Union, Any, Optional
import os


VALID_FLAG_VALUE_TYPES = [int, float, str, None]

#Base class for representing a Bash Executable Flag
@dataclass(frozen=True)
class BashExecFlag:

    flag : str
    value_types : Union[Type, list[Type], None] = field(hash=False)

    value_is_numeric : bool = False
    value_is_alphabetic : bool = False
    value_is_file : bool = False
    file_exists : bool = False

    value_range : Optional[Range] = field(default=None, hash=False)
    value_prefix : Optional[str] = field(default=None, hash=True)
    value_suffix : Optional[str] = field(default=None, hash=True)

    def __post_init__(self):
        
        #Validate that value types are either int, float, str, or None
        self._validate_flag()
            
    def bash_format(self, value=None) -> str:
        #Validate the value
        try:
            self._validate_value(value)
        except Exception as e:
            raise e

        #Edge case 1: If value is none just return the flag
        if value is None:
            return self.flag

        #Edge case 2: If flag is empty, do not append '='.
        if len(self.flag) == 0:
            flag_str = ''
        else:
            flag_str = f'{self.flag}='

        # Format value with provided prefix and suffix
        complete_val = f'{self.value_prefix}{value}{self.value_suffix}'

        bash_str = ""
        if type(value) == int or type(value) == float:
            bash_str = f'{flag_str}{complete_val}'
        elif type(value) == str:
            bash_str = f'{flag_str}"{complete_val}"'

        return bash_str
    

    def _validate_flag(self):
        #Convert single value type to list to reduce code repetition
        flag_types = self.value_types
        if not isinstance(self.value_types, list):
            flag_types = [self.value_types]
        
        for flag_type in flag_types:
            if flag_type not in VALID_FLAG_VALUE_TYPES:
                raise AttributeError(f"Flag Value Type must be one of '[{", ".join(VALID_FLAG_VALUE_TYPES)}]'. Got {flag_type}")
            
        #Additional check if user specified at least a (flag of length > 0) and / or (a value that is not None)
        if len(self.flag) == 0 and None in flag_types:
            raise AttributeError(f"Cannot have a Zero length flag with a None type value")
        
        #Additional check to ensure user Flag is enforced to be (numeric or alphabetic) or (numeric or file), not both.
        if self.value_is_numeric and self.value_is_alphabetic:
            raise AttributeError(f"Value cannot be both numeric and alphabetic")
        
        if self.value_is_numeric and self.value_is_file:
            raise AttributeError(f"Value cannot be both numeric and a file path")
        
        #Additional check to see if value_is_file is True if file_exists is specified as True
        if self.file_exists and not self.value_is_file:
            raise AttributeError(f"Value")

    def _validate_value(self, value=None):

        try:
            self._validate_value_type(value)
            self._validate_numeric(value)
            self._validate_in_range(value)
            self._validate_alphabetic(value)
            self._validate_file_path(value)
            self._validate_file_exists(value)
        except Exception as e:
            raise e
        
    def _validate_value_type(self, value):
        flag_types = self.value_types
        value_type = type(value)
        if not isinstance(self.value_types, list):
            flag_types = [self.value_types]
        if value_type not in flag_types: # type: ignore
            raise Exception(f"Value type must be one of [{", ".join(flag_types)}]. Got {value_type}") # type: ignore

    #Check if value must be numeric
    def _validate_numeric(self, value):
        if self.value_is_numeric and not isinstance(value, numbers.Number):
            raise Exception(f"value must be convertible to a number. Got {value}")

    def _validate_alphabetic(self, value):
        if self.value_is_alphabetic and (not isinstance(value, str) or not value.isalpha()):
            raise Exception(f"value must be a non numeric string. Got {value}")

    def _validate_file_path(self, value):
        if self.value_is_file:
            try:
                os.path.normpath(value)
            except Exception as e:
                raise e
            
    def _validate_in_range(self, value):
        if self.value_range:
            try:
                self.value_range.validate(value)
            except Exception as e:
                raise e
            
            
    def _validate_file_exists(self, value):
        if self.file_exists:
            try:
                exists = os.path.exists(value)
                if not exists:
                    raise AttributeError(f"File at '{value}' does not exist")
            except Exception as e:
                raise e

#Base class for representing a bash executable
@dataclass
class BashExecutable:

    executable : str = field(default="", init=True)
    _flag_container: Optional[Any] = field(default=None, init=False)
    flag_value_dict : Dict[BashExecFlag, Union[numbers.Number, str, None]] = field(default_factory=dict, init=False)
    last_flag : BashExecFlag = None # type: ignore

    def flags(self):
        _flags = []
        for _field in fields(self._flag_container):
            attr = getattr(self._flag_container, _field.name)
            if isinstance(attr, BashExecFlag):
                _flags.append(attr)
        return _flags

    def set_flag_val(self, flag : BashExecFlag, value : Union[numbers.Number, str, None]):
        executable_flags = self.flags()
        if flag not in executable_flags:
            raise AttributeError(f"Flag '{flag}' is not a flag for this executable. The following flags are available:") #TODO: Add string representation
        self.flag_value_dict[flag] = value

    def set_all_flags_vals(self, flag_value_dictionary : Dict[BashExecFlag, Union[numbers.Number, str, None]]):
        self.flag_value_dict = flag_value_dictionary

    def generate_cmd(self):
        executable_string = f'{self.executable} '
        for flag, value in self.flag_value_dict.items():
            #Do not add specified last flag until the end
            if flag is not self.last_flag:
                executable_string += f'{flag.bash_format(value)} '
        if self.last_flag:
            last_val = self.flag_value_dict.items()
            executable_string += f'{self.last_flag.bash_format(last_val)}'
        return executable_string

    def __post_init__(self):

        if self._flag_container is not None and not is_dataclass(self._flag_container):
            raise Exception("Provided flag container must be a dataclass.")

