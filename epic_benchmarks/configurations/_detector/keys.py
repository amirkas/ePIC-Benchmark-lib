from dataclasses import dataclass, fields, field
from typing import Dict, List, Any
from epic_benchmarks.configurations._config import ConfigKey, ConfigKeyContainer
from epic_benchmarks.configurations._detector.types import DetectorConfigType
from epic_benchmarks.configurations._detector.xpath import DetectorConfigXpath

@dataclass
class DetectorKeyContainer:

    file : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="file",
        types=str,
        default="Test"
    ))
    config_type : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="edit_type",
        types=[str, DetectorConfigType],
        default=DetectorConfigType.SET
    ))
    detector_attributes : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="detector_attributes",
        types=Dict[str, str]
    ))
    module_attributes : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="module_attributes",
        types=Dict[str, str]
    ))
    module_component_attributes : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="module_component_attributes",
        types=Dict[str, str]
    ))
    update_attribute : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="update_attribute",
        types=str,
    ))
    update_value : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="update_value",
        types=Any,
    ))




