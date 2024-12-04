
DETECTOR_SET_CMD = "set"
DETECTOR_ADD_CMD = "add"
DETECTOR_DELETE_CMD = "delete"
DETECTOR_CONFIG_TYPES = (DETECTOR_SET_CMD, DETECTOR_ADD_CMD, DETECTOR_DELETE_CMD)

BENCHMARK_DETECTOR_CONFIG_KEY = "detector_config"
DETECTOR_FILE_KEY = "file"
DETECTOR_TYPE_KEY = "type"
DETECTOR_NAME_KEY = "detector_name"
DETECTOR_MODULE_KEY = "module_name"
DETECTOR_MODULE_COMPONENT_KEY = "module_component"
DETECTOR_ATTRIBUTE_KEY = "attribute"
DETECTOR_VALUE_KEY = "value"

DETECTOR_KEYS = [
    DETECTOR_FILE_KEY,
    DETECTOR_TYPE_KEY,
    DETECTOR_NAME_KEY,
    DETECTOR_MODULE_KEY,
    DETECTOR_MODULE_COMPONENT_KEY,
    DETECTOR_ATTRIBUTE_KEY,
    DETECTOR_VALUE_KEY
]

DETECTOR_ELEM_SPECIFIERS = [DETECTOR_NAME_KEY, DETECTOR_MODULE_KEY, DETECTOR_MODULE_COMPONENT_KEY]


class DetectorConfig:

    def __init__(self, load_config_dict=None, config_type=None, detector_file_name=None,
            detector_element_name=None, module_name=None,
            module_component_name=None, attribute=None, value=None):
        
        if load_config_dict != None:
            if not isinstance(load_config_dict, dict):
                raise Exception("Detector config to load must be a Python Dictionary")
            for key, value in load_config_dict.items():
                if key in DETECTOR_KEYS:
                    setattr(self, key, value)

            #Add loading validation
                

        else:
            if config_type == None:
                raise Exception("Detector Configuration type must be specified")

            if detector_file_name == None:
                raise Exception("Filename for detector must be specified")

            if not isinstance(config_type, str):
                raise Exception("Config type must be a string")
            
            if config_type not in DETECTOR_CONFIG_TYPES:
                raise Exception("Config type must be one of the following: ", DETECTOR_CONFIG_TYPES)
            
            #User must specify at least one of the following for any detector config type:
            #   - 'detector_name', 
            #   - 'module_name'
            #   - 'module_component'

            config_type = config_type.lower()

            if detector_element_name == None and module_name == None and module_component_name == None:
                raise Exception("Access specifier must be an argument to find elements to update")
            
            if attribute == None:
                raise Exception("'attribute' must be an argument")

            setattr(self, DETECTOR_TYPE_KEY, config_type)
            setattr(self, DETECTOR_FILE_KEY, detector_file_name)
            setattr(self, DETECTOR_NAME_KEY, detector_element_name)
            setattr(self, DETECTOR_MODULE_KEY, module_name)
            setattr(self, DETECTOR_MODULE_COMPONENT_KEY, module_component_name)
            setattr(self, DETECTOR_ATTRIBUTE_KEY, attribute)

            if config_type == DETECTOR_CONFIG_TYPES[0] or config_type == DETECTOR_CONFIG_TYPES[1]:
                if value == None:
                    raise Exception("'value' must be an argument for 'set' or 'add' config types")
                setattr(self, DETECTOR_VALUE_KEY, value)


    def get_config_dict(self):

        config = {}
        for k, v in self.__dict__.items():
            if k in DETECTOR_KEYS:
                config[k] = v
        return config



    
