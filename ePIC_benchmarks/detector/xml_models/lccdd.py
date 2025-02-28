from ePIC_benchmarks.detector.xml_models._base import BaseDetectorDescriptionModel
from pydantic_xml import element, attr


class lccdd(BaseDetectorDescriptionModel):

    info : str = element()
    includes : str = element()
    define : str = element()
    materials : str = element()
    display : str = element()
    detectors : str = element()
    readouts : str = element()
    limits : str = element()
    fields : str = element()
