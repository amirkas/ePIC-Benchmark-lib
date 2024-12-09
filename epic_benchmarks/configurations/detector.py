from epic_benchmarks.configurations._config import BaseConfig, ConfigMetaClass
from epic_benchmarks.configurations._detector.keys import DetectorKeyContainer
from epic_benchmarks.configurations._detector.types import DetectorConfigType


class DetectorConfig(BaseConfig):

    _config_key_container = DetectorKeyContainer()

    def foo(self):
        # print(f"\n\n{self.__class__.__dict__}")
        # print(f"\n\\n{self.update_value}")]
        # print(self.__class__.__dict__)
        pass

config = DetectorConfig(
    {
    'file' : "tracking/silicon_disks.xml",
    'detector_attributes' : {"name" : "InnerTrackerEndcapP"},
    'module_attributes' : {"name" : "Module1"},
    'module_component_attributes' : {"material" : "Silicon"},
    'update_attribute' : "sensitive",
    'update_value' : False
    },
    load_filepath=None
)



# print(DetectorKeyContainer().keys())

# print(getattr(DetectorConfig, '_config_key_container', None))
# print(DetectorConfig.__annotations__)




        
