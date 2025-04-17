from pydantic import BaseModel, Field, PlainSerializer
from typing import Literal, Dict, Optional, Union, ClassVar, Annotated
from ePIC_benchmarks.detector.xml_elements._base import (
    XmlElement, AnnotatedOptionalBool, AnnotatedOptionalString
)

class XmlSegmentationElement(XmlElement):

    element_tag : Literal['segmentation'] = Field(default='segmentation', init=False)
    
    #Attributes

    type : AnnotatedOptionalString
    grid_size_x : AnnotatedOptionalString
    grid_size_y : AnnotatedOptionalString

    update_attribute : Optional[Literal['type', 'grid_size_x', 'grid_size_y']] = None
    

class XmlReadoutIdElement(XmlElement):

    element_tag : Literal['id'] = Field(default='id', init=False)

class XmlReadoutElement(XmlElement):

    element_tag : Literal['readout'] = Field(default='readout', init=False)

    #Attributes
    name : AnnotatedOptionalString
    
    update_attribute : Optional[Literal['name']] = None

    #Sub-elements
    segmentation : Optional[XmlSegmentationElement] = None




