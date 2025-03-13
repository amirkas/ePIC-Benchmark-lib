import yaml
import json

#Supported file extensions for configurations and their associated dump routines
FILE_EXTENSION_DUMP_MAP = {
    '.yml' : lambda content, file : yaml.safe_dump(content, file, sort_keys=False),
    ".yaml" : lambda content, file : yaml.safe_dump(content, file, sort_keys=False),
    ".json" : lambda content, file : json.dump(content, file, sort_keys=False),
}

#Supported file extensions for configurations and their associated load routines
FILE_EXTENSION_LOAD_MAP = {
    ".yml" : lambda file : yaml.safe_load(file),
    ".yaml" : lambda file : yaml.safe_load(file),
    ".json" : lambda file : json.load(file),
}

#Ensures the File extension dump map and load map have the same file extensions
assert(set(FILE_EXTENSION_DUMP_MAP.keys()) == set(FILE_EXTENSION_LOAD_MAP.keys()))

SUPPORTED_FILE_EXTENSIONS = FILE_EXTENSION_DUMP_MAP.keys()
DEFAULT_CONFIG_FILE_EXT = ".yml"