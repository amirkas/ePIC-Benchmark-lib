import yaml
import json


FILE_EXTENSION_DUMP_MAP = {
    '.yml' : lambda content, file : yaml.safe_dump(content, file, sort_keys=False),
    ".yaml" : lambda content, file : yaml.safe_dump(content, file, sort_keys=False),
    ".json" : lambda content, file : json.dump(content, file, sort_keys=False),
}

FILE_EXTENSION_LOAD_MAP = {
    ".yml" : lambda file : yaml.safe_load(file),
    ".yaml" : lambda file : yaml.safe_load(file),
    ".json" : lambda file : json.load(file),
}

SUPPORTED_FILE_EXTENSIONS = FILE_EXTENSION_DUMP_MAP.keys()
DEFAULT_CONFIG_FILE_EXT = ".yml"