from pydantic import (
    BaseModel, Field, PlainSerializer, RootModel, ConfigDict, SerializeAsAny
)
from typing import (
    Literal, Dict, Optional, Union, ClassVar, Annotated, Sequence
)
from ePIC_benchmarks.detector.xml_elements._base import (
    XmlElement, XmlElementList,
    AnnotatedOptionalBool, AnnotatedOptionalString, AnnotatedOptionalInt
)

class XmlModuleComponentElement(XmlElement):

    element_tag : Literal['module_component'] = Field(default='module_component', init=False)

    #Attributes
    name : AnnotatedOptionalString
    material : AnnotatedOptionalString
    sensitive : AnnotatedOptionalBool
    width : AnnotatedOptionalString
    length : AnnotatedOptionalString
    thickness : AnnotatedOptionalString
    vis : AnnotatedOptionalString
    reflect : AnnotatedOptionalBool

    update_attribute : Optional[Literal[
        'name', 'material', 'sensitive',
        'width', 'length', 'thickness',
        'vis', 'reflect'
    ]] = None

XmlModuleComponentList = XmlElementList[XmlModuleComponentElement]

class XmlFrameElement(XmlElement):

    element_tag : Literal['frame'] = Field(default='frame', init=False)    

    #Attributes
    material : AnnotatedOptionalString
    vis : AnnotatedOptionalString
    width : AnnotatedOptionalString
    height : AnnotatedOptionalString
    length : AnnotatedOptionalString
    thickness : AnnotatedOptionalString

    update_attribute : Optional[Literal[
        'material', 'vis', 'width', 'height', 'length', 'thickness'
    ]]

class XmlTrdElement(XmlElement):

    element_tag : Literal['trd'] = Field(default='trd', init=False)
    
    #Attributes
    x1 : AnnotatedOptionalString
    x2 : AnnotatedOptionalString
    z : AnnotatedOptionalString

    update_attribute : Optional[Literal['x1', 'x2', 'z']] = None


class XmlModuleElement(XmlElement):

    element_tag : Literal['module'] = Field(default='module', init=False)

    #Attributes
    name : AnnotatedOptionalString
    vis : AnnotatedOptionalString

    update_attribute : Optional[Literal['name', 'vis']] = None

    module_components : Union[
        None, XmlModuleComponentElement, XmlModuleComponentList
    ] = None
    trd : Optional[XmlTrdElement] = None
    frame : Optional[XmlFrameElement] = None

XmlModuleList = XmlElementList[XmlModuleElement]

class XmlTypeFlagsElement(XmlElement):

    element_tag : Literal['type_flags'] = Field(default='type_flags', init=False)

    #Attributes
    type : AnnotatedOptionalString
    update_attribute : Optional[Literal['type']] = None

class XmlDimensionsElement(XmlElement):

    element_tag : Literal['dimensions'] = Field(default='dimensions', init=False)

    #Attributes
    rmin : AnnotatedOptionalString
    rmax : AnnotatedOptionalString
    length : AnnotatedOptionalString

    update_attribute : Optional[Literal['rmin', 'rmax', 'length']] = None

class XmlLayerMaterialElement(XmlElement):

    element_tag : Literal['layer_material'] = Field(default='layer_material', init=False)

    #Attributes
    surface : AnnotatedOptionalString
    binning : AnnotatedOptionalString
    bins0 : AnnotatedOptionalString
    bins1 : AnnotatedOptionalString

    update_attribute : Optional[Literal[
        'surface', 'binning', 'bins0', 'bins1'
    ]] = None
    
XmlLayerMaterialList = XmlElementList[XmlLayerMaterialElement]

class XmlRphiLayoutElement(XmlElement):

    element_tag : Literal['rphi_layout'] = Field(default='rphi_layout', init=False)

    #Attributes
    phi_tilt : AnnotatedOptionalString
    nphi : AnnotatedOptionalString
    phi0 : AnnotatedOptionalString
    rc : AnnotatedOptionalString
    dr : AnnotatedOptionalString

    update_attribute : Optional[Literal[
        'phi_tilt', 'nphi', 'phi0', 'rc', 'dr'
    ]] = None

class XmlZLayoutElement(XmlElement):

    element_tag : Literal['z_layout'] = Field(default='z_layout', init=False)

    #Attributes
    dr : AnnotatedOptionalString
    z0 : AnnotatedOptionalString
    nz : AnnotatedOptionalString

    update_attribute : Optional[Literal[
        'dr', 'z0', 'nz'
    ]] = None

class XmlBarrelEnvelopeElement(XmlElement):

    element_tag : Literal['barrel_envelope'] = Field(default='barrel_envelope', init=False)

    #Attributes
    inner_r : AnnotatedOptionalString
    outer_r : AnnotatedOptionalString
    z_length : AnnotatedOptionalString

    update_attribute : Optional[Literal[
        'inner_r', 'outer_r', 'z_length'
    ]] = None

class XmlEnvelopeElement(XmlElement):

    element_tag : Literal['envelope'] = Field(default='envelope', init=False)

    #Attributes
    vis : AnnotatedOptionalString
    rmin : AnnotatedOptionalString
    rmax : AnnotatedOptionalString
    length : AnnotatedOptionalString
    zstart : AnnotatedOptionalString

    update_attribute : Optional[Literal[
        'vis', 'rmin', 'rmax', 'length', 'zstart'
    ]] = None

class XmlRingElement(XmlElement):

    element_tag : Literal['ring'] = Field(default='ring', init=False)

    r : AnnotatedOptionalString
    zstart : AnnotatedOptionalString
    nmodules : AnnotatedOptionalString
    dz : AnnotatedOptionalString
    module : AnnotatedOptionalString

    update_attribute : Optional[Literal[
        'r', 'zstart', 'nmodules', 'dz', 'module'
    ]] = None
    

class XmlLayerElement(XmlElement):

    element_tag : Literal['layer'] = Field(default='layer', init=False)

    #Attributes
    module : AnnotatedOptionalString
    id : AnnotatedOptionalInt
    vis : AnnotatedOptionalString

    update_attribute : Optional[Literal['module', 'id', 'vis']] = None

    #Sub-elements
    barrel_envelope : Optional[XmlBarrelEnvelopeElement] = None
    layer_material : Optional[Union[XmlLayerMaterialElement, XmlLayerMaterialList]] = None
    rphi_layout : Optional[XmlRphiLayoutElement] = None
    z_layout : Optional[XmlZLayoutElement] = None
    envelope : Optional[XmlEnvelopeElement] = None
    ring : Optional[XmlEnvelopeElement] = None

XmlLayerList = XmlElementList[XmlLayerElement]

class XmlDetectorElement(XmlElement):

    element_tag : Literal['detector'] = Field(default='detector', init=False)

    #Attributes
    id : AnnotatedOptionalString
    name : AnnotatedOptionalString
    type : AnnotatedOptionalString
    insideTrackingVolume : AnnotatedOptionalBool

    update_attribute : Optional[
        Literal['id', 'name', 'type', 'insideTrackingVolume']
    ] = None

    #Sub-elements
    modules : Optional[Union[XmlModuleElement, XmlModuleList]] = None
    type_flags : Optional[XmlTypeFlagsElement] = None
    dimensions : Optional[XmlDimensionsElement] = None
    layers : Optional[Union[XmlLayerElement, XmlLayerList]] = None