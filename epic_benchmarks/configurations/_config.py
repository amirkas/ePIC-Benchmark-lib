from __future__ import annotations
from collections.abc import Iterable
import copy
from dataclasses import dataclass, fields, field, is_dataclass
import os
import yaml
from typing import Type, Callable, List, Any, Optional, ClassVar, Self, Dict

@dataclass(kw_only=True)
class ConfigKey:

    # Name of the key that will be used as the tag in a configuration file
    key_name : str

    # Types that configuration value can have
    types : Type | List[Type]

    # Default value for configuration
    default : Optional[Any] = field(default=None, init=True)

    # Boolean indicating that a value must be provided for
    # this configuration parameter
    optional : Optional[bool] = field(default=True, init=True)

    # A callable that takes in the configuration value and returns a correctly formatted one
    formatter : Optional[Callable[[Any], Any]] = field(default=None, init=True)

    # A callable that takes in a configuration value and does extra validation beyond type and optional checking
    validator : Optional[Callable[[Any], bool]] = field(default=None, init=True)

    # A dictionary to store metadata associated with a config key
    # Example: BashExecFlags
    metadata : Optional[Dict[Any, Any]] = field(default_factory=dict, init=True)

    # Indicates that this configuration key is associated with a configuration instance value.
    # Nested configs allow 1 configuration class to have multiple sub-configuration classes
    nested_config : Optional[BaseConfig] | None = field(default=None, init=True)

    # Internal field that stores the current value associated with the key.
    _current_value : Optional[Any] = field(default=False, init=False)

    # Internal field indicating whether the key has been externally set.
    _value_set : bool = field(default=False, init=False)


    def __post_init__(self):

        #If no types are provided in types list raise Exception.
        if isinstance(self.types, list) and len(self.types) == 0:
            raise Exception("Must provide at least one type. Can be 'Any' type.")

        #If optional and default not provided, create an appropriate default
        if self.optional and self.default is None:
            if isinstance(self.types, list):
                object_type = self.types[0]
            else:
                object_type = self.types
            if isinstance(object_type, type):
                self.default = object_type()
            elif hasattr(object_type, '__origin__'):
                self.default = object_type.__origin__()

        #Validate default value
        self.validate(self.default, ignore_optional=True)

        #Set current_value to the default value
        self.current_value = self.default

    def update_value(self, value):
        try:
            self.validate(value)
        except Exception as e:
            raise e
        self._value_set = True
        self._current_value = self.format(value)

    def get_value(self):
        return self._current_value

    def is_optional(self) -> bool:
        return self.optional

    def value_updated(self) -> bool:
        return self._value_set

    def format(self, value):
        if self.formatter:
            return self.formatter(value)
        return value

    #TODO: Refactor function into components
    def validate(self, value, ignore_optional=False):
        type_list = self.types
        #Early check if value is optional and is none
        if value is None and self.optional:
            return
        if not isinstance(self.types, list):
            type_list = [self.types]
        valid_type_found = False
        for t in type_list:
            #Break early
            if t is Any:
                valid_type_found = True
                break
            #Handle primitive types
            if isinstance(t, type) and isinstance(value, t):
                valid_type_found = True
                break
            #Handle non-primitive types
            elif hasattr(t, "__origin__") and isinstance(value, t.__origin__):
                valid_type_found = True
                break
        if not valid_type_found:
            if not self.optional and not self._value_set and not ignore_optional:
                err = f"'{self.key_name}' is a non-Optional configuration which must be provided a value."
                raise TypeError(err)
            elif not self.optional and not self._value_set and ignore_optional:
                pass
            else:
                err = (f"Config key '{self.key_name}' has value '{value}' which must"
                       f" have one of the following type(s):"
                       f" [{" ".join(map(str, type_list))}]. Got '{str(type(value))}'"
                )
                raise TypeError(err)
        if self.validator:
            try:
                is_valid = self.validator(value)
            except Exception as e:
                raise e
            if not is_valid:
                err = f"Validation failed for key {self.key_name} with value {value}"
                raise ValueError(err)
           

@dataclass(kw_only=True)
class BaseConfig:

    load_dict : Optional[Dict[str, Any]] = field(init=True, default=None)
    load_filepath : Optional[str] = field(init=True, default=None)
    _key_attribute_names : List[str] = field(default_factory=list, init=False)

    #Supported Files for loading and saving
    YML_EXT = ".yml"
    YAML_EXT = ".yaml"
    XML_EXT = ".xml"

    def keys(self):
        return copy.deepcopy(self._key_attribute_names)
    
    def property_exists(self, key):
        return key in self.keys()

    def property_value(self, key):
        config_key = self._config_key(key)
        return config_key.get_value()

    def property_default(self, key):
        config_key = self._config_key(key)
        return config_key.default

    def property_metadata(self, key):
        config_key = self._config_key(key)
        return config_key.metadata

    def property_updated(self, key):
        config_key = self._config_key(key)
        return config_key.value_updated()

    def to_dict(self):
        config_dict = {}
        for key in self.keys():
            val = getattr(self, key)
            if isinstance(val, BaseConfig):
                val = val.to_dict()
            elif isinstance(val, list):
                val = self._to_dict_iter_helper(val)
            config_dict[key] = val
        return config_dict






    # Private methods
    def _to_dict_iter_helper(self, lst : list):

        assert isinstance(lst, list)
        parsed = []
        for item in lst:
            if isinstance(item, BaseConfig):
                parsed.append(item.to_dict())
            elif isinstance(item, list):
                nested_list = self._to_dict_iter_helper(item)
                parsed.append(nested_list)
            else:
                parsed.append(item)
        return parsed


    # Gets the configuration key associated with 'key'
    def _config_key(self, key):
        key_names = self.keys()
        keys = [getattr(self, n) for n in key_names]
        for _key in keys:
            if isinstance(_key, ConfigKey) and _key.key_name == key:
                return _key
        raise ValueError(f"Key '{key}' not found")


    # Retrieves the nested config class associated with a key.from.from
    # Return class type if key found and class exists, otherwise none.from
    # Throws exception if config key doesn't exist.
    def _nested_config(self, key) -> ConfigKey:
        try:
            config_key = self._config_key(key)
        except ValueError:
            return None
        if config_key:
            return config_key.nested_config
        return None

    def _load_params(self, **kwargs):

        for key in self.keys():
            val = kwargs[key]
            nested_config = self._nested_config(key)
            #Recursively initializes nested configurations if key is associated with a config
            if nested_config and isinstance(val, dict):
                new_config = nested_config(load_dict=val)
                setattr(self, key, new_config)
            elif nested_config and isinstance(val, list):
                nested_lst = self._load_params_iter_helper(nested_config, val)
                setattr(self, key, nested_lst)
            #If not a config, just set the value in the dictionary
            else:
                setattr(self, key, val)

    def _load_params_iter_helper(self, nested_config, lst : list):

        assert isinstance(lst, list)
        parsed = []
        for item in lst:
            if nested_config and isinstance(item, dict):
                new_config = nested_config(load_dict=item)
                parsed.append(new_config)
            elif isinstance(item, list):
                nested_list = self._load_params_iter_helper(nested_config, item)
                parsed.append(nested_list)
            else:
                parsed.append(item)
        return parsed

    def _load_dict(self, load_dict : dict) -> None:
        self._load_params(**load_dict)

    # Loads a configuration from any supported file type
    # Currently supported file extensions:
    #   - .yml
    def _load_from_file(self, filepath):
        if os.path.exists(filepath):
            file_ext = os.path.splitext(filepath)[-1]
            match file_ext:
                case str(YML_EXT):
                    self._load_yml_file(yml_filepath=filepath)
                #Add additional supported File extensions here
                case _:
                    err = f"File with extension '{file_ext}' is not a valid file type."
                    raise Exception(err)
        else:
            err = f"File at path '{filepath}' does not exist."
            raise Exception(err)

    # Loads a configuration via the dictionary pulled from a yml file.
    def _load_yml_file(self, yml_filepath):
        try:
            with open(yml_filepath, 'r') as f:
                yml_data = yaml.safe_load(yml_filepath)
                self._load_params(**yml_data)
        except Exception as e:
            raise e

    # Parses through input arguments, validates them, and sets their associated attributes
    def __post_init__(self):

        if self.load_dict:
            self._load_dict(self.load_dict)

        elif self.load_filepath:
            self._load_from_file(filepath=self.load_filepath)

        #Populate config keys list and validate all non-optional arguments are set.
        for _field in fields(self):
            if _field.type == ConfigKey:
                self._key_attribute_names.append(_field.name)
                config_key = object.__getattribute__(self, _field.name)
                #Non-optional validation
                try:
                    config_key.validate(config_key.get_value(), ignore_optional=False)
                except Exception as e:
                    raise e


    # Custom getter that retrieves the value held by a name's associated config key
    # If the associated attribute is not a config key, use default getter.
    def __getattribute__(self, name: str) -> Any:

        attr = object.__getattribute__(self, name)
        if isinstance(attr, ConfigKey):
            return attr.get_value()

        return super().__getattribute__(name)


    # Custom setter that sets input values in the config key associated with the name
    # Does not affect attributes that aren't config key instances
    def __setattr__(self, name: str, value: Any):

        if hasattr(self, name):
            attr = object.__getattribute__(self, name)
            if isinstance(attr, ConfigKey):
                attr.update_value(value)
                return
        if not hasattr(self, name) and name in self.__dataclass_fields__ and type(value) != ConfigKey:
            _field = self.__dataclass_fields__[name]
            if _field.type == ConfigKey:
                config_key = _field.default_factory()
                assert isinstance(config_key, ConfigKey)
                config_key.update_value(value)
                super().__setattr__(name, config_key)
                return

        super().__setattr__(name, value)
