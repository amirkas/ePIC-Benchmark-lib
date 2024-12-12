from ctypes import ArgumentError
from dataclasses import dataclass, fields
import os
from epic_benchmarks.configurations import BaseConfig, BaseConfigKeys
from epic_benchmarks.configurations.utils import XmlEditor

@dataclass
class DetectorConfigType:

    SET : str = "set"
    ADD : str = "add"
    DELETE : str = "delete"
    
@dataclass    
class DetectorConfigXpath:

    ROOT_TAG : str = "."
    DETECTOR_TAG : str = "detector"
    MODULE_TAG : str = "module"
    COMPONENT_TAG : str = "module_component"

    @classmethod
    def create_tag_query(cls, tag, attributes) -> str:
        if not isinstance(attributes, dict):
            raise ArgumentError("attributes must be a dictionary: Got type: ", type(attributes))
        if len(tag) == 0:
            return ""
        query = f'//{tag}'
        if len(attributes.keys()) > 0:
            attr_str = lambda item : f"@{item[0]}='{item[1]}'"
            all_attr_str = " && ".join(map(attr_str, list(attributes.items())))
            query += f'[{all_attr_str}]'
        return query
    
    @classmethod
    def create_generic_query(cls, query_elems : dict) -> str:

        combined_query = ''
        for tag, attributes in query_elems.items():
            combined_query += cls.create_tag_query(tag, attributes)
        return combined_query
    
    @classmethod
    def create_query(cls, detector_attributes, module_attributes, module_component_attributes):
        return cls.create_generic_query(
            {
            cls.DETECTOR_TAG : detector_attributes,
            cls.MODULE_TAG : module_attributes,
            cls.COMPONENT_TAG : module_component_attributes
            }
        )

    
    @classmethod
    def detector_tag_query(cls, attributes):
        return cls.create_tag_query(cls.DETECTOR_TAG, attributes)
    
    
    @classmethod
    def module_tag_query(cls, attributes):
        return cls.create_tag_query(cls.MODULE_TAG, attributes)
    
    @classmethod
    def module_component_tag_query(cls, attributes):
        return cls.create_tag_query(cls.COMPONENT_TAG, attributes)
    

@dataclass
class DetectorConfigKeys(BaseConfigKeys):

    BENCHMARK_CONFIG_KEY : str = "detector_config"

    FILE : str = "file"
    CONFIG_TYPE : str = "type"
    
    DETECTOR_ATTRIBUTES : str = "detector_attributes"
    MODULE_ATTRIBUTES : str = "module_attributes"
    MODULE_COMPONENT_ATTRIBUTES : str = "module_component_attributes"

    UPDATE_ATTRIBUTE : str = "update_attribute"
    UPDATE_VALUE : str = "update_value"

    @classmethod
    def keys(cls):
        return cls.__dict__.keys()
    
    @classmethod
    def hasKey(cls, k):
        return k in cls.keys()

class DetectorConfig(BaseConfig):

    def __init__(self, load_config_dict=None, config_type=None, detector_file_name=None,
            detector_attributes={}, module_attributes={},
            module_component_attributes={}, update_attribute=None, update_value=None):
        
        args_valid, err = self._validate_args(
            load_config_dict, config_type, detector_file_name,
            detector_attributes, module_attributes, module_component_attributes,
            update_attribute, update_value
        )
        if not args_valid:
            raise ArgumentError(err)
        
        if load_config_dict is not None:
            for key, value in load_config_dict.items():
                if DetectorConfigKeys.hasKey(key):
                    setattr(self, key, value)
        else:

            setattr(self, DetectorConfigKeys.CONFIG_TYPE, config_type)
            setattr(self, DetectorConfigKeys.FILE, detector_file_name)
            setattr(self, DetectorConfigKeys.DETECTOR_ATTRIBUTES, detector_attributes)
            setattr(self, DetectorConfigKeys.MODULE_ATTRIBUTES, module_attributes)
            setattr(self, DetectorConfigKeys.MODULE_COMPONENT_ATTRIBUTES, module_component_attributes)
            setattr(self, DetectorConfigKeys.UPDATE_ATTRIBUTE, update_attribute)

            if config_type == DetectorConfigType.SET or config_type == DetectorConfigType.ADD:
                setattr(self, DetectorConfigKeys.UPDATE_VALUE, update_value)


    def get_config_dict(self):

        config = {}
        for k, v in self.__dict__.items():
            if DetectorConfigKeys.hasKey(k):
                config[k] = v
        return config
    
    def xpath_search_query(self):
        query = ''
        detector_attributes = getattr(self, DetectorConfigKeys.DETECTOR_ATTRIBUTES)
        module_attributes = getattr(self, DetectorConfigKeys.MODULE_ATTRIBUTES)
        module_component_attributes = getattr(self, DetectorConfigKeys.MODULE_COMPONENT_ATTRIBUTES)
        
        return DetectorConfigXpath.create_query(detector_attributes, module_attributes, module_component_attributes)
    
    def apply_update(self, directory_path):

        filename = getattr(self, DetectorConfigKeys.FILE)
        xml_filepath = os.path.join(directory_path, filename)
        editor = XmlEditor(xml_filepath, autosave=False)

        query = self.xpath_search_query()
        update_attribute = getattr(self, DetectorConfigKeys.UPDATE_ATTRIBUTE)
        config_type = getattr(self, DetectorConfigKeys.CONFIG_TYPE)

        try:
            if config_type == DetectorConfigType.SET:
                update_value = getattr(self, DetectorConfigKeys.UPDATE_VALUE)
                editor.set_attribute_xpath(query, update_attribute, update_value)
            elif config_type == DetectorConfigType.ADD:
                #TODO: Add implementation
                pass
            elif config_type == DetectorConfigType.DELETE:
                #TODO: Add implementation
                pass
            editor.save()
        except:
            raise Exception("Could not apply changes for:\n", str(self))

    def _validate_args(self, load_config_dict, config_type, detector_file_name,
                       detector_attributes, module_attributes, module_component_attributes,
                       update_attribute, update_value):

        err_msg = ''
        is_valid = True
        if load_config_dict is not None and load_config_dict is not isinstance(load_config_dict, dict):
            is_valid, err_msg = False, f"If specified, Detector config to load must be a Dictionary. Got type: {load_config_dict}"
        elif config_type is None:
            is_valid, err_msg = False, "Detector Configuration type must be specified"
        elif detector_file_name is None:
            is_valid, err_msg = False, "Filename for detector must be specified"
        elif not DetectorConfigType.isValidType(config_type):
            is_valid, err_msg = False, f"Config type must be one of the following: {DetectorConfigType.allAttributes()}. Got '{config_type}'"
        elif update_attribute is None:
            is_valid, err_msg = False, "'update_attribute' must be an argument"
        elif not isinstance(update_attribute, str):
            is_valid, err_msg = False, f"'update_attribute' must be a string. Got type: {update_attribute}"
        elif not isinstance(detector_attributes, dict):
            is_valid, err_msg = False, f"Detector attributes must be a dictionary. Got type: {type(detector_attributes)}"
        elif not isinstance(module_attributes, dict):
            is_valid, err_msg = False, f"Module attributes must be a dictionary. Got type: {type(module_attributes)}"
        elif not isinstance(module_component_attributes, dict):
            is_valid, err_msg = False, f"Module component attributes must be a dictionary.  Got type: {type(module_component_attributes)}"
        elif (config_type == DetectorConfigType.SET or config_type == DetectorConfigType.ADD) and update_value == None:
            is_valid, err_msg = False, "'update_value' must be an argument for 'set' or 'add' config types"

        return is_valid, err_msg

    def _validate_load_dict(self, load_dict):
        # TODO: Implement load dictionary validation
        pass

    def __repr__(self):

        type_str = f"Configuration Type: {getattr(self, DetectorConfigKeys.CONFIG_TYPE)}"
        filename_str = f"File name : {getattr(self, DetectorConfigKeys.FILE)}"

        detector_attributes = getattr(self, DetectorConfigKeys.DETECTOR_ATTRIBUTES)
        module_attributes = getattr(self, DetectorConfigKeys.MODULE_ATTRIBUTES)
        module_component_attributes = getattr(self, DetectorConfigKeys.MODULE_COMPONENT_ATTRIBUTES)

        detector_attributes_tuples = list(detector_attributes.items())
        module_attributes_tuples = list(module_attributes.items())
        module_component_attributes_tuples = list(module_component_attributes.items())

        attr_str_func = lambda item: f"(attribute: {item[0]}, value: {item[1]})"
        detector_attr_str = f"Detector Attributes: [{" ".join(map(attr_str_func, detector_attributes_tuples))}]"
        module_attr_str = f"Module Attributes: [{" ".join(map(attr_str_func, module_attributes_tuples))}]"
        component_attr_str = f"Module Component Attributes: [{" ".join(map(attr_str_func, module_component_attributes_tuples))}]"

        update_attribute_str = getattr(self, DetectorConfigKeys.UPDATE_ATTRIBUTE)
        update_value_str = getattr(self, DetectorConfigKeys.UPDATE_VALUE)

        combined_str = f"{type_str}\n{filename_str}\n{detector_attr_str}\n{module_attr_str}\n{component_attr_str}\n{update_attribute_str}\n{update_value_str}"
        return combined_str


        




    
