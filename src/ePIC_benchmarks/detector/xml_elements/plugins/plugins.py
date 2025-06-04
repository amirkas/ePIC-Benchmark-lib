from pydantic import BaseModel, Field, PlainSerializer
from typing import Literal, Dict, Optional, Union, ClassVar, Annotated
from ePIC_benchmarks.detector.xml_elements._base import (
    XmlElement, XmlElementList,
    AnnotatedOptionalBool, AnnotatedOptionalString
)

class XmlArgumentElement(XmlElement):

    element_tag : Literal[''] = Field(default='', init=False)

    #Attributes
    value : AnnotatedOptionalString

    update_attribute : Optional[Literal['value']] = None

XmlArgumentList = XmlElementList[XmlArgumentElement]

class XmlPluginElement(XmlElement):

    element_tag : Literal['plugin'] = Field(default='plugin', init=False)

    #Attributes
    name : AnnotatedOptionalString

    update_value : Optional[Literal['name']] = None
    