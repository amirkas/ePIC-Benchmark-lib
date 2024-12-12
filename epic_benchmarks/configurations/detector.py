import os
from typing import Any, Dict

from epic_benchmarks.configurations import XmlEditor
from epic_benchmarks.configurations._config import BaseConfig, ConfigKey
from epic_benchmarks.configurations._detector.types import DetectorConfigType
from epic_benchmarks.configurations._detector.xpath import DetectorConfigXpath
from dataclasses import dataclass, fields, field

@dataclass
class DetectorConfig(BaseConfig):

    file: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="file",
        types=str,
        optional=False,
    ))
    edit_type: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="edit_type",
        types=[str, DetectorConfigType],
        default=DetectorConfigType.SET,
        optional=True,
        validator=lambda x: isinstance(x, DetectorConfigType),
    ))
    detector_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="detector_attributes",
        types=Dict[str, str],
        optional=True,
    ))
    module_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="module_attributes",
        types=Dict[str, str],
        optional=True,
    ))
    module_component_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="module_component_attributes",
        types=Dict[str, str],
        optional=True,
    ))
    update_attribute: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="update_attribute",
        types=str,
        optional=False,
    ))
    update_value: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
        key_name="update_value",
        types=Any,
        optional=True,
    ))

    def xpath_query(self):

        query = DetectorConfigXpath.create_query(
            self.detector_attributes,
            self.module_attributes,
            self.module_component_attributes
        )
        return query

    def apply_config(self, directory_path):

        xml_filepath = os.path.join(directory_path, self.file)
        if not os.path.exists(xml_filepath):
            err = f"{xml_filepath} does not exist"
            raise ValueError(err)
        xml_editor = XmlEditor(xml_filepath, autosave=False)
        query = self.xpath_query()

        attribute = self.update_attribute
        value = self.update_value
        match self.edit_type:
            case DetectorConfigType.SET:
                xml_editor.set_attribute_xpath(query, attribute, value)
            case DetectorConfigType.ADD:
                raise NotImplemented()
            case DetectorConfigType.DELETE:
                raise NotImplemented()
        xml_editor.save()

    def __post_init__(self):

        #Call base class post init
        super().__post_init__()

        #Extra Config Validation
        #1) If type is set or add, an update value must be provided.
        if self.edit_type == DetectorConfigType.ADD or self.edit_type == DetectorConfigType.SET:
            pass


