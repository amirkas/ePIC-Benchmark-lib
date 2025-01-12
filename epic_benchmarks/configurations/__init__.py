#For testing on windows
# import multiprocessing
# multiprocessing.set_start_method('spawn', force=True)


from ._simulation.types import *
from ._detector.types import DetectorConfigType
from .utils.file_config import YamlEditor, XmlEditor
from .simulation import SimulationConfig
from .detector import DetectorConfig
from .benchmark import BenchmarkConfig
from .benchmark_suite import BenchmarkSuiteConfig
from .parsl_config import ParslConfig
import json
import yaml

FILE_EXTENSION_DUMP_MAP = {
    '.yml' : lambda content, file : yaml.safe_dump(content, file),
    ".yaml" : lambda content, file : yaml.safe_dump(content, file),
    ".json" : lambda content, file : json.dump(content, file),
}

FILE_EXTENSION_LOAD_MAP = {
    ".yml" : lambda file : yaml.safe_load(file),
    ".yaml" : lambda file : yaml.safe_load(file),
    ".json" : lambda file : json.load(file),
}

SUPPORTED_FILE_EXTENSIONS = FILE_EXTENSION_DUMP_MAP.keys()
DEFAULT_CONFIG_FILE_EXT = ".yml"

__all__ = [
    'SimulationConfig',
    'DetectorConfig',
    'BenchmarkConfig',
    'BenchmarkSuiteConfig',
    'DetectorConfigType',
    'ParslConfig',
    'YamlEditor',
    'XmlEditor',
    FILE_EXTENSION_DUMP_MAP,
    FILE_EXTENSION_LOAD_MAP,
    SUPPORTED_FILE_EXTENSIONS,
    DEFAULT_CONFIG_FILE_EXT
]
