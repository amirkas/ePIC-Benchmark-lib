from __future__ import annotations
from dataclasses import dataclass, fields, field, is_dataclass
import os
import yaml
import copy
from typing import Type, Callable, List, Any, Optional, ClassVar, Self, Dict
from collections.abc import Iterable

XML_EXT = ".xml"
YML_EXT = ".yml"

CONFIG_CONTAINER_ATTR = '_config_key_container'
CONFIG_LIST_ATTR = '_config_keys'
ANNOTATIONS_KEY = '__annotations__'

@dataclass 
class ConfigKey:

    key_name : str
    types : Type | List[Type]
    default : Any = None
    optional : bool = True
    factory : Optional[Callable[[Any], Any]] = None
    validator : Optional[Callable[[Any], bool]] = None
    metadata : Optional[Dict[Any, Any]] = field(default_factory=dict)
    nested_config : Optional[BaseConfig] | None = None

    def __post_init__(self):

        #If no types are provided in types list raise Exception.
        if isinstance(self.types, list) and len(self.types) == 0:
            raise Exception("Must provide at least one type. Can be 'Any' type.")

        #If not optional and default not provided, create an appropiate default
        if not self.optional and self.default is None:
            if isinstance(self.types, list):
                first_type = self.types[0]
                self.default = first_type()
            else:
                self.default = self.types()

        #Validate default value
        self.validate(self.default)


    def format(self, value):
        if self.factory:
            return self.factory(value)
        return value
    
    def validate(self, value):
        type_list = self.types
        #Early check if value is optional and is none
        if value is None and self.optional:
            return
        if not isinstance(self.types, list):
            type_list = [self.types]
        for t in type_list: # type: ignore
            #Continue early
            if t is Any:
                continue
            #Handle primitive types
            if isinstance(t, type) and not isinstance(value, t):
                err = f"Config key '{self.key_name} has value '{value}' which must have one of the following type(s): [{" ".join(map(str, type_list))}]. Got '{str(type(value))}'"
                raise TypeError(err)
            #Handle non-primitive types
            elif hasattr(t, "__origin__"):
                origin = t.__origin__
                if not isinstance(value, origin):
                    err = f"Config key '{self.key_name} has value '{value}' which must have one of the following type(s): [{" ".join(map(str, type_list))}]. Got '{str(type(value))}'"
                    raise TypeError(err)
        if self.validator:
            try:
                is_valid = self.validator(value)
            except Exception as e:
                raise e
            if not is_valid:
                err = f"Validation failed for key {self.key_name} with value {value}"
                raise ValueError(err)
           
@dataclass
class ConfigKeyContainer:

    # @classmethod
    # def keys(cls) -> List[ConfigKey]:
    #     return [field.default for field in fields(cls) if isinstance(field.default, ConfigKey)]
    
    def keys(self) -> List[ConfigKey]:
        return [key for key in self.__dict__.values() if isinstance(key, ConfigKey)]

class ConfigMetaClass(type):

    def __new__(cls, name, bases, namespace):

        key_container = None
        key_list = None
        if CONFIG_CONTAINER_ATTR in namespace.keys():
            key_container = namespace[CONFIG_CONTAINER_ATTR]

        if CONFIG_LIST_ATTR in namespace.keys():
            key_list = namespace[CONFIG_LIST_ATTR]

        class_instance = super().__new__(cls, name, bases, namespace)

        if key_container:
            config_key_lst = key_container.keys()
            setattr(class_instance, CONFIG_LIST_ATTR, config_key_lst)
        elif key_list:
            config_key_lst = key_list
        else:
            config_key_lst = []

        if ANNOTATIONS_KEY not in namespace.keys():
            namespace[ANNOTATIONS_KEY] = {}

        setattr(class_instance, "_metadata", {})
        namespace["_metadata"] = {}
        for config_key in config_key_lst:
            

            #Populate annotations for autocomplete
            cls._populate_annotations(namespace, class_instance, config_key)

            #Update setter and getter for config key property
            cls._set_property_handlers(namespace, class_instance, config_key)

            cls._set_metadata_map(class_instance, config_key)

            cls._set_metadata_getter(namespace, class_instance, config_key)

        cls._define_dir(namespace, class_instance, config_key_lst)

        return class_instance


    def __call__(cls, *args, load_dict=None, load_filepath=None, **kwargs):

        key_container = getattr(cls, '_config_key_container', None)
        key_lst = getattr(cls, '_config_keys', [])

        if key_container:
            config_key_lst = key_container.keys()
        else:
            config_key_lst = key_lst

        instance = super().__call__(*args, **kwargs)

        for config_key in config_key_lst:

            #Set Default Attribute Values
            cls._set_default(instance, config_key)

        return instance


    #Populate annotations for autocomplete
    @staticmethod
    def _populate_annotations(namespace, instance, config_key : ConfigKey):

        attribute_name = config_key.key_name
        attribute_types = config_key.types
        
        cls_local = object.__getattribute__(instance, '__class__')
        if not hasattr(cls_local, ANNOTATIONS_KEY):
            cls_local.__annotations__ = {}

        cls_local.__annotations__[attribute_name] = attribute_types
        instance.__annotations__[attribute_name] = attribute_types
        namespace[ANNOTATIONS_KEY][attribute_name] = attribute_types

    @staticmethod
    def _define_dir(namespace, instance, config_key_list : List[ConfigKey]):
        
        def __dir__(self):
            return list(self.__class__.__annotations__.keys())

        instance.__dir__ = __dir__

    @staticmethod
    def _set_property_handlers(namespace, instance, config_key : ConfigKey):

        attribute_name = config_key.key_name

        def property_handlers(key : ConfigKey):

            def getter(self):
                return getattr(self, f"_{key.key_name}", key.default)
            
            def setter(self, value):
                key.validate(value)
                formatted_val = key.format(value)
                setattr(self, f"_{key.key_name}", formatted_val)

            return property(getter, setter)
        
        namespace[attribute_name] = property_handlers(config_key)
        setattr(instance, attribute_name, property_handlers(config_key))


    @staticmethod
    def _set_metadata_map(instance, config_key : ConfigKey):

        instance._metadata[config_key.key_name] = config_key.metadata


    @staticmethod
    def _set_metadata_getter(namespace, instance, config_key : ConfigKey):

        def metadata_handler(config_key : ConfigKey):

            def getter(self):

                metadata = getattr(self, "_metadata_map", {})
                return metadata[config_key.key_name]
            
            return getter
        
        func_str = f"get_{config_key.key_name}_Metadata"
        namespace[func_str] = metadata_handler(config_key)
        setattr(instance, func_str, metadata_handler(config_key))


    @staticmethod
    def _set_default(instance, config_key : ConfigKey):

        if not hasattr(instance, config_key.key_name):
            setattr(instance, config_key.key_name, config_key.default)


@dataclass
class BaseConfig(metaclass=ConfigMetaClass):

    _config_key_container : ClassVar[Optional[ConfigKeyContainer]] = ConfigKeyContainer()
    _config_keys : ClassVar[List[ConfigKey]] = []
    _metadata_map : ClassVar[Dict[str, Any]] = {}

    #Public methods

    def __init__(self, load_dict : dict, load_filepath=None, **kargs):
        
        if load_dict:
            self._load_dict(load_dict)
        
        elif load_filepath:
            self._load_from_file(filepath=load_filepath)

        self._load_params(**kargs)

    def keys(self):
        return [key.key_name for key in self._config_keys]
    
    def isKey(self, key):
        return key in self.keys()
    
    def value(self, key):
        try:
            return copy.deepcopy(getattr(self, key))
        except Exception as e:
            raise e
    
    def keyMetadata(self, key):
        try:
            return copy.deepcopy(self._metadata_map[key])
        except Exception as e:
            raise e

    def toDict(self):
        config_dict = {}
        for key in self.keys():
            val = getattr(self, key)
            if isinstance(type(val), BaseConfig):
                val = val.to_dict()
            config_dict[key] = val
        return config_dict
    
    #Private methods

    def _config_key(self, key):
        for config_key in self._config_keys:
            if key == config_key.key_name:
                return config_key
        raise Exception(f"Key '{key}' not found")

    def _nested_config(self, key):
        try:
            config_key = self._config_key(key)
        except Exception as e:
            raise e
        if config_key:
            return config_key.nested_config
        return None

    def _load_params(self, **kargs):
        for key, val in kargs.items():
            if key in self.keys():
                nested_config = self._nested_config(key)
                #Recursively initializes nested configurations if key is associated with a config
                if nested_config and isinstance(val, dict):
                    new_config = nested_config(load_dict=val)
                #If not a config, just set the value in the dictionary
                else:
                    setattr(self, key, val)

    def _load_dict(self, load_dict : dict) -> None:
        self._load_params(**load_dict)

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
    
    def _load_yml_file(self, yml_filepath):
        try:
            with open(yml_filepath, 'r') as f:
                yml_data = yaml.safe_load(yml_filepath)
                self._load_params(**yml_data)
        except Exception as e:
            raise e
        

    def __getattribute__(self, name: str) -> Any:


        cls = object.__getattribute__(self, '__class__')
        annotations = object.__getattribute__(cls, '__annotations__')
        formatted_name = f"_{name}"

        if name in annotations and formatted_name in self.__dict__:
            return self.__dict__[formatted_name]

        return object.__getattribute__(self, name)

        # formatted_name = f"_{name}"
        # if formatted_name in self.__class__.__annotations__:
        #     return self.__dict__.get(formatted_name, None)
        # raise AttributeError("Attribute not found")
        
    # def combineAsCopy(self, other : BaseConfig) -> BaseConfig:
    #     self_copy = copy.deepcopy(self)
    #     for key, val in other.items():
    #         if not self.isKey(key):
    #             setattr(self_copy, key, copy.deepcopy(val))
        
    #     return self_copy



        

    


# @dataclass
# class BaseConfigKeys:

#     @classmethod
#     def allKeys(cls):
#         return [field.name for field in fields(cls)]
    
#     @classmethod
#     def items(cls):
#         return [(field.name, field.default) for field in fields(cls)]
    
#     @classmethod
#     def isKey(cls, key):
#         return key in cls.allKeys()
    
#     @classmethod
#     def keyField(cls, key):
#         for field in fields(cls):
#             if field.name == key:
#                 return field
#         return None
    
#     @classmethod
#     def valueType(cls, key):
#         field = cls.keyField(key)
#         if field is None:
#             raise AttributeError(f"Key '{key}' is not an attribute of ")   
#         return field.type

#     @classmethod
#     def keyDefault(cls, attribute):
#         field = cls.keyField(attribute)
#         if field is None:
#             raise AttributeError(f"Key '{attribute}' is not an attribute of ")   
#         return field.default
    
#     #Further validation for attribute value. Defaults to throwing an exception and should be overriden by inherited classes.
#     @classmethod
#     def isValidValue(cls, key, val):
#         raise NotImplementedError("Inherited Class must implement definition for this method")
    
#     #Formats value of the value of some key. Can be overriden by inherited classes to format unique key-value pairs.
#     @classmethod
#     def formatValue(cls, key, val):
#         return val

#     @classmethod
#     def isValidArgument(cls, key, val):
#         field = cls.keyField(key)
#         if field is None:
#             raise AttributeError(f"Key '{key}' is not an attribute of ")
#         field_type = field.type
#         return isinstance(val, field_type) and cls.isValidValue(key, val)

            
#     @classmethod
#     def validateArgs(cls, **kargs):
#         for key, val in kargs.items():
#             if not cls.isValidArgument(key, val):
#                 val_type = cls.valueType(key)
#                 raise AttributeError(f"Value of Key '{key}' must have type '{val_type}'. Got '{type(val)}'")




# @dataclass
# class BaseConfig:

#     key_dataclass : BaseConfigKeys

#     def __init__(self, load_dict : dict, load_filepath=None, **kargs):

#         #Validate args before setting instance attributes
#         self._validate_args(**kargs)

#         #Set default values for all instance attributes
#         self._init_default_params()

#         #Load Dictionary if one is given
#         if load_dict:
#             #Validate load dictionary before setting instance attributes
#             self._validate_args(**load_dict)
#             self._load_dict(load_dict)

#         #Load file if one is given
#         if load_filepath:
#             pass

#         #Validate args before setting instance attributes
#         self._validate_args(**kargs)

#         #Load all other arguments
#         self._load_params(**kargs)

#     def items(self):
#         all_items = {}
#         for field in fields(self):
#             if field.name is not "key_dataclass":
#                 key = field.name
#                 value = getattr(self, key)
#                 all_items[key] = value
#         return all_items
    
#     def isKey(self, key):
#         return hasattr(self, key)
    
#     def combine(self, other : BaseConfig):
#         for key, val in other.items():
#             if not self.isKey(key):
#                 #TODO: Implement behaviour for iterable vals
#                 setattr(self, key, copy.deepcopy(val))

#     def combineAsCopy(self, other : BaseConfig):
#         self_copy = copy.deepcopy(self)
#         self_copy.combine(other)
#         return self_copy

#     def _validate_args(self, **kargs):
#         try:
#             self.key_dataclass.validateArgs(**kargs)
#         except AttributeError as e:
#             raise e
        
#     def _init_default_params(self):
#         for key, default in self.key_dataclass.items():
#             setattr(self, key, default)
        
#     def _load_params(self, **kargs):
#         for key, val in kargs.items():
#             formatted_val = self.key_dataclass.formatValue(key, val)
#             setattr(self, key, formatted_val)
    
#     def _load_dict(self, load_dict : dict):
#         self._load_params(**load_dict)

#     def _load_from_file(self, filepath):
#         if os.path.exists(filepath):
#             file_ext = os.path.splitext(filepath)[-1]
#             match file_ext:
#                 case str(YML_EXT):
#                     self._load_yml_file(yml_filepath=filepath)
#                 #Add additional supported File extensions here
#                 case _:
#                     raise Exception(f"File with extension '{file_ext}' is not a valid file type.")
#         else:
#             raise Exception(f"File at path '{filepath}' does not exist.")
        
#     def _load_yml_file(self, yml_filepath):
#         try:
#             with open(yml_filepath, 'r') as f:
#                 yml_data = yaml.safe_load(yml_filepath)
#                 self._load_params(**yml_data)
#         except Exception as e:
#             raise e
        
#     #Annotate subclass init method for IDE autocompletion
#     def __init_subclass__(cls, **kwargs):
#         super().__init_subclass__(**kwargs)
#         sub_key_dataclass = getattr(cls, 'key_dataclass', None)
#         if sub_key_dataclass and is_dataclass(sub_key_dataclass):
#             cls.__annotations__ = {field.name : field.type for field in fields(sub_key_dataclass)}

#     #Return dictionary format for the config instance, which recursively class on member config instances.
#     def to_dict(self):

#         config_dict = {}
#         for key in self.key_dataclass.allKeys():
#             val = getattr(self, key)
#             if isinstance(type(val), BaseConfig):
#                 val = val.to_dict()
#             config_dict[key] = val
#         return config_dict

    
