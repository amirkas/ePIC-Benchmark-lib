from ePIC_benchmarks.detector import DetectorConfig
from ePIC_benchmarks.detector.xml_elements.detector import (
    XmlDetectorElement, XmlModuleElement,
    XmlModuleComponentElement, XmlFrameElement,
)

EXAMPLE_DETECTOR_CONFIG = DetectorConfig(
    file="tracking/silicon_disks.xml",
    edit_element_trees=XmlDetectorElement(
        name="InnerTrackerEndcapP",
        modules=XmlModuleElement(
            name="Module1",
            module_components=XmlModuleComponentElement(
                material="Silicon",
                update_attribute="sensitive",
                update_value="false",
                update_type='SET'
            )
        )
    )
)