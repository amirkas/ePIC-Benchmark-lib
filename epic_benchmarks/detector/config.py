from pathlib import Path
from typing import Any, Dict, Union, Optional, Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator, computed_field

from epic_benchmarks._file.editors import XmlEditor
from epic_benchmarks.detector.types import DetectorConfigType
from epic_benchmarks.detector.xpath import DetectorConfigXpath
from epic_benchmarks._file.types import PathType

class DetectorConfig(BaseModel):

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True, validate_default=True)

    file : PathType
    edit_type : Union[str, DetectorConfigType]
    detector_attributes : Optional[Dict[str, str]]
    module_attributes: Optional[Dict[str, str]]
    module_component_attributes: Optional[Dict[str, str]]
    update_attribute : str
    update_value : Optional[Any]

    @field_validator('file', mode='after')
    def validate_file(cls, v : Any) -> Any:
        #TODO: Check whether filepath is in a readable directory
        # if not is_file_path_readable(v):
        #     raise ValueError('File path is not readable')
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

    def apply_changes(self, directory_path : Optional[PathType]=None):

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