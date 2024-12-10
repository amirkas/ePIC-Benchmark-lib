from typing import Any, Dict

from epic_benchmarks.configurations._config import BaseConfig, ConfigKey
from epic_benchmarks.configurations._detector.types import DetectorConfigType
from dataclasses import dataclass, fields, field

@dataclass
class DetectorConfig(BaseConfig):

    file: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="file",
        types=str,
    ))
    edit_type: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="edit_type",
        types=[str, DetectorConfigType],
        default=DetectorConfigType.SET
    ))
    detector_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="detector_attributes",
        types=Dict[str, str]
    ))
    module_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="module_attributes",
        types=Dict[str, str]
    ))
    module_component_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="module_component_attributes",
        types=Dict[str, str]
    ))
    update_attribute: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="update_attribute",
        types=str,
    ))
    update_value: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="update_value",
        types=Any,
    ))

