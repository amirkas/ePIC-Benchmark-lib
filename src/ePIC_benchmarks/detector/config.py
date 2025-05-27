from pathlib import Path
from typing import Any, Dict, Union, Optional, Self, Literal, Sequence, Annotated

from pydantic import (
    BaseModel, ConfigDict, field_validator, model_serializer,
    model_validator, Field, RootModel, SerializeAsAny
)

from ePIC_benchmarks._file.editors import XmlEditor
from ePIC_benchmarks.detector.types import DetectorConfigType
from ePIC_benchmarks.detector.xpath import DetectorConfigXpath
from ePIC_benchmarks.detector.xml_elements._base import XmlElement, XmlElementList
from ePIC_benchmarks.detector.xml_elements.detector import *
from ePIC_benchmarks.detector.xml_elements.constant import *
from ePIC_benchmarks.detector.xml_elements.plugins import *
from ePIC_benchmarks.detector.xml_elements.readout import *
from ePIC_benchmarks._file.types import PathType


XmlElementUnion = Union[
    XmlDetectorElement, XmlModuleElement, XmlModuleComponentElement,
    XmlLayerElement, XmlLayerMaterialElement, XmlRphiLayoutElement, XmlTrdElement,
    XmlDimensionsElement, XmlRingElement, XmlEnvelopeElement, XmlBarrelEnvelopeElement,
    XmlTypeFlagsElement, XmlZLayoutElement, XmlFrameElement, XmlConstantElement,
    XmlPluginElement, XmlArgumentElement,
    XmlReadoutElement, XmlSegmentationElement, XmlReadoutIdElement
]

XmlElementDiscriminator = Annotated[XmlElementUnion, Field(discriminator='element_tag')]

class XmlElementDiscriminatedList(RootModel):
    
    model_config = ConfigDict(strict=True)
    root : SerializeAsAny[Sequence[XmlElementDiscriminator]]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

class DetectorConfig(BaseModel):

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True, validate_default=True,)

    file : PathType = Field(
        description=(
            "Path of the detector description xml file to be updated,"
            " relative to the compact folder of the ePIC repository."
        )
    )

    edit_element_trees : Union[XmlElementDiscriminator, XmlElementDiscriminatedList]

    def apply_changes(self, directory_path : Optional[PathType]=None):

        xml_path = Path(self.file)
        if directory_path:
            if isinstance(directory_path, str):
                directory_path = Path(directory_path)
            elif isinstance(directory_path, Path):
                directory_path = directory_path
            else:
                raise ValueError("Directory path must be a valid path")
            xml_path = directory_path.joinpath(xml_path)
        if not xml_path.exists():
            err = f"Path '{xml_path}' does not exist"
            raise ValueError(err)

        try:
            xml_editor = XmlEditor(xml_path, autosave=False)
        except:
            err = f"Could not load file '{xml_path}'"
            raise ValueError(err)

        queries = self._all_queries()

        for q in queries:

            xml_query, update_attribute, update_type, update_value = q
            match update_type:
                case "SET":
                    try:
                        xml_editor.set_attribute_xpath(xml_query, update_attribute, update_value)
                    except:
                        err = (
                            f"could not make update with:\n[\n"
                            f"    Query: {xml_query}\n"
                            f"    Update Attribute: {update_attribute}\n"
                            f"    Update Value: {update_value}\n]"
                        )
                        raise ValueError(err)
                case "ADD":
                    raise NotImplementedError()
                case "DELETE":
                    raise NotImplementedError()
                
            try:
                xml_editor.save()
            except:
                err = f"Could not save updated xml file '{xml_path}'"
                raise ValueError(err)
        
    def _all_queries(self):

        queries = []
        if not hasattr(self.edit_element_trees, '__iter__'):
            for query in self.edit_element_trees.create_queries():
                queries.append(query)
        else:
            for element_tree in self.edit_element_trees:
                for query in element_tree.create_queries():
                    queries.append(query) 
        return queries
    
    #Validates whether the detector description file is valid
    @field_validator('file', mode='after')
    def validate_file(cls, v : Any) -> Any:
        #TODO: Check whether filepath is in a readable directory
        # if not is_file_path_readable(v):
        #     raise ValueError('File path is not readable')
        if not isinstance(v, str):
            return str(v)
        return v
    
    @field_validator('edit_element_trees', mode='before')
    def validate_edit_trees(cls, v : Any) -> Any:
        if not isinstance(v, list):
            return [v]
        return v
    
class DetectorConfigOld(BaseModel):

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

    #Validates whether the detector description file is valid
    @field_validator('file', mode='after')
    def validate_file(cls, v : Any) -> Any:
        #TODO: Check whether filepath is in a readable directory
        # if not is_file_path_readable(v):
        #     raise ValueError('File path is not readable')
        if not isinstance(v, str):
            return str(v)
        return v

    #Casts edit type to string if it is an instance of DetectorConfigType
    @field_validator('edit_type', mode='before')
    def validate_edit_type(cls, v : Any) -> str:
        if isinstance(v, DetectorConfigType):
            return v.value
        return v

    #Ensures that an update value is passed if edit type is 'SET' or 'ADD'
    @model_validator(mode='after')
    def check_update_value_required(self) -> Self:
        if self.update_value is None:
            if self.edit_type == "SET":
                raise ValueError("Update Value must be specified for set operation")
            elif self.edit_type == "ADD":
                raise ValueError("Update Value must be specified for add operation")
        return self
    
    #Serializes the model to a python dictionary
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

    #Generates the xpath query used to find the xml element to be updated.
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

    #Applies the update to the detector description file located at 'file'
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

