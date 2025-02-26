from pathlib import Path
from typing import Any, Dict, Union, Optional, Self, Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_serializer, model_validator, Field

from epic_benchmarks._file.editors import XmlEditor
from epic_benchmarks.detector.types import DetectorConfigType
from epic_benchmarks.detector.xpath import DetectorConfigXpath
from epic_benchmarks._file.types import PathType


class DetectorConfig(BaseModel):

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True, validate_default=True,)

    file : PathType = Field(
        description=(
            "Path of the detector description xml file to be updated,"
            " relative to the compact folder of the ePIC repository."
        )
    )
    edit_type : Literal["SET", "ADD", "DELETE"] = Field(description="Type of edit to detector description.")
    detector_attributes : Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Dictionary of {attribute name : attribute value} pairs"
            " for a <detector> element that is either"
            " the ancestor of element to be updated,"
            " or the element to be updated itself."
        ),
        examples=[
            '{"name" : "SagittaSiBarrel"}'
        ]
    )
    module_attributes : Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Dictionary of {attribute name : attribute value} pairs"
            " for a <module> element that is either"
            " the ancestor of element to be updated,"
            " or the element to be updated itself."
        )
    )
    module_component_attributes : Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Dictionary of {attribute name : attribute value} pairs"
            " for a <component> element that is either"
            " the ancestor of element to be updated,"
            " or the element to be updated itself."
        )
    )
    constant_attributes : Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Dictionary of {attribute name : attribute value} pairs"
            " for a <constant> element that is either"
            " the ancestor of element to be updated,"
            " or the element to be updated itself."
        )
    )
    readout_attributes : Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Dictionary of {attribute name : attribute value} pairs"
            " for a <readout> element that is either"
            " the ancestor of element to be updated,"
            " or the element to be updated itself."
        )
    )
    segmentation_attributes : Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Dictionary of {attribute name : attribute value} pairs"
            " for a <segmentation> element that is either"
            " the ancestor of element to be updated,"
            " or the element to be updated itself."
        )
    )

    update_attribute : str = Field(
        description="Name of the attribute of an xml element to be updated"
    )
    update_value : Optional[Any] = Field(
        default=None,
        description=(
            "The desired value to be set for the attribute given"
            " by 'update_attribute' for the 'SET' edit type. OR"
            " The desired value to be added for the attribute given"
            " by 'update_attribute' for the 'ADD' edit type. OR"
        )
    )

    @field_validator('file', mode='after')
    def validate_file(cls, v : Any) -> Any:
        #TODO: Check whether filepath is in a readable directory
        # if not is_file_path_readable(v):
        #     raise ValueError('File path is not readable')
        if not isinstance(v, str):
            return str(v)
        return v

    @field_validator('edit_type', mode='before')
    def validate_edit_type(cls, v : Any) -> str:
        if isinstance(v, DetectorConfigType):
            return v.value
        return v

    @model_validator(mode='after')
    def check_update_value_required(self) -> Self:
        if self.update_value is None:
            if self.edit_type == DetectorConfigType.SET.value:
                raise ValueError("Update Value must be specified for set operation")
            elif self.edit_type == DetectorConfigType.ADD.value:
                raise ValueError("Update Value must be specified for add operation")
        return self
    
    @model_serializer(mode='wrap')
    def serialize_detector_config(self, handler) -> Dict[Any, Any]:

        serialized_dict = {
            "file" : self.file,
            "edit_type" : self.edit_type
        }
        optional_dict = {
            "detector_attributes" : self.detector_attributes,
            "module_attributes" : self.module_attributes,
            "module_component_attributes" : self.module_component_attributes,
            "constant_attributes" : self.constant_attributes,
            "readout_attributes" : self.readout_attributes,
            "segmentation_attributes" : self.segmentation_attributes,
        }
        for key, val in optional_dict.items():
            if val is not None:
                serialized_dict[key] = val
        serialized_dict["update_attribute"] = self.update_attribute
        serialized_dict["update_value"] = self.update_value
        
        return serialized_dict


    @property
    def xpath_query(self) -> str:

        query = DetectorConfigXpath.create_query(
            self.detector_attributes,
            self.module_attributes,
            self.module_component_attributes,
            self.constant_attributes,
            self.readout_attributes,
            self.segmentation_attributes
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
            case "SET":
                xml_editor.set_attribute_xpath(self.xpath_query, attribute, value)
            case "ADD":
                raise NotImplemented()
            case "DELETE":
                raise NotImplemented()
        xml_editor.save()