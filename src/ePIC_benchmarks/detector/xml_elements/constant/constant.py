from pydantic import BaseModel, Field, PlainSerializer
from typing import Literal, Dict, Optional, Union, ClassVar, Annotated
from ePIC_benchmarks.detector.xml_elements._base import (
    XmlElement, AnnotatedOptionalBool, AnnotatedOptionalString
)

from typing import ClassVar, Literal

class XmlConstantElement(XmlElement):

    element_tag : Literal['constant'] = Field(default='constant', init=False)

    #Attributes
    name : AnnotatedOptionalString
    value : AnnotatedOptionalString

    update_attribute : Optional[Literal['name', 'value']] = None
    