import os
from pathlib import Path
from typing import Any, Dict, Union, Optional, Self

from pydantic import BaseModel, field_validator, model_validator, computed_field

from epic_benchmarks.configurations._validators import path_exists, is_file_path_readable
from epic_benchmarks.configurations import XmlEditor
from epic_benchmarks.configurations._config import ConfigurationModel
from epic_benchmarks.configurations._detector.types import DetectorConfigType
from epic_benchmarks.configurations._detector.xpath import DetectorConfigXpath

class DetectorConfig(ConfigurationModel):

    file : str
    edit_type : Union[str, DetectorConfigType]
    detector_attributes : Optional[Dict[str, str]]
    module_attributes: Optional[Dict[str, str]]
    module_component_attributes: Optional[Dict[str, str]]
    update_attribute : str
    update_value : Optional[Any]

    @field_validator('file', mode='after')
    def validate_file(cls, v : Any) -> Any:
        if not is_file_path_readable(v):
            raise ValueError('File path is not readable')
        return v

    @field_validator('edit_type', mode='before')
    def validate_edit_type(cls, v : Any) -> str:
        if isinstance(v, DetectorConfigType):
            return v.value
        elif isinstance(v, str):
            for edit_t in DetectorConfigType:
                if edit_t.value == v:
                    return v
            err = f"{v} is not a valid edit type"
            raise ValueError(err)
        else:
            raise ValueError("edit type must be a string or DetectorConfigType")

    @model_validator(mode='after')
    def check_update_value_required(self) -> Self:
        if self.update_value is None:
            if self.edit_type == DetectorConfigType.SET.value:
                raise ValueError("Update Value must be specified for set operation")
            elif self.edit_type == DetectorConfigType.ADD.value:
                raise ValueError("Update Value must be specified for add operation")


    @computed_field
    @property
    def xpath_query(self) -> str:

        query = DetectorConfigXpath.create_query(
            self.detector_attributes,
            self.module_attributes,
            self.module_component_attributes
        )
        return query

    def apply_changes(self, directory_path=None):

        xml_path = Path(self.file)
        if directory_path:
            if isinstance(directory_path, str):
                directory_path = Path(directory_path)
            elif isinstance(directory_path, Path):
                directory_path = directory_path.resolve()
            else:
                raise ValueError("Directory path must be a valid path")
            xml_path = directory_path.joinpath(xml_path)
        if not xml_path.exists():
            raise ValueError("Path does not exist")

        xml_editor = XmlEditor(xml_path, autosave=False)
        attribute = self.update_attribute
        value = self.update_value
        match self.edit_type:
            case DetectorConfigType.SET:
                xml_editor.set_attribute_xpath(self.xpath_query, attribute, value)
            case DetectorConfigType.ADD:
                raise NotImplemented()
            case DetectorConfigType.DELETE:
                raise NotImplemented()
        xml_editor.save()

#
#
# @dataclass
# class TestDetectorConfig(BaseConfig):
#
#     file: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
#         key_name="file",
#         types=str,
#         optional=False,
#     ))
#     edit_type: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
#         key_name="edit_type",
#         types=[str, DetectorConfigType],
#         default=DetectorConfigType.SET,
#         optional=True,
#         validator=lambda x: isinstance(x, DetectorConfigType),
#     ))
#     detector_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
#         key_name="detector_attributes",
#         types=Dict[str, str],
#         optional=True,
#     ))
#     module_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
#         key_name="module_attributes",
#         types=Dict[str, str],
#         optional=True,
#     ))
#     module_component_attributes: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
#         key_name="module_component_attributes",
#         types=Dict[str, str],
#         optional=True,
#     ))
#     update_attribute: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
#         key_name="update_attribute",
#         types=str,
#         optional=False,
#     ))
#     update_value: ConfigKey = field(init=False, default_factory=lambda: ConfigKey(
#         key_name="update_value",
#         types=Any,
#         optional=True,
#     ))
#
#     def xpath_query(self):
#
#         query = DetectorConfigXpath.create_query(
#             self.detector_attributes,
#             self.module_attributes,
#             self.module_component_attributes
#         )
#         return query
#
#     def apply_config(self, directory_path):
#
#         xml_filepath = os.path.join(directory_path, self.file)
#         if not os.path.exists(xml_filepath):
#             err = f"{xml_filepath} does not exist"
#             raise ValueError(err)
#         xml_editor = XmlEditor(xml_filepath, autosave=False)
#         query = self.xpath_query()
#
#         attribute = self.update_attribute
#         value = self.update_value
#         match self.edit_type:
#             case DetectorConfigType.SET:
#                 xml_editor.set_attribute_xpath(query, attribute, value)
#             case DetectorConfigType.ADD:
#                 raise NotImplemented()
#             case DetectorConfigType.DELETE:
#                 raise NotImplemented()
#         xml_editor.save()
#
#     def __post_init__(self):
#
#         #Call base class post init
#         super().__post_init__()
#
#         #Extra Config Validation
#         #1) If type is set or add, an update value must be provided.
#         if self.edit_type == DetectorConfigType.ADD or self.edit_type == DetectorConfigType.SET:
#             pass
#
#
