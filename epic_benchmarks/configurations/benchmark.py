from dataclasses import dataclass, fields, field
from typing import Optional, List, Dict, Any

from epic_benchmarks.configurations import BaseConfig, ConfigKey
from epic_benchmarks.configurations.detector import DetectorConfig
from epic_benchmarks.configurations.simulation import SimulationConfig, CommonSimulationConfig

@dataclass
class BenchmarkConfig(BaseConfig):
    epic_branch: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="epic_branch",
        types=[str],
        default="main",
        optional=True,
    ))
    detector_configs: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="detector_configs",
        types=Optional[List[Dict[str, Any] | DetectorConfig]],
        optional=True,
        nested_config=DetectorConfig
    ))
    common_simulation_config: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="common_simulation_config",
        types=Optional[Dict[str, Any] | CommonSimulationConfig],
        optional=False,
        nested_config=CommonSimulationConfig
    ))
    simulation_configurations: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="simulation_configurations",
        types=Optional[List[Dict[str, Any] | SimulationConfig]],
        default=[],
        optional=True,
        nested_config=SimulationConfig
    ))

    def set_common_simulation_config(self):
        raise NotImplementedError()

    def add_detector_config(self):
        raise NotImplementedError()

    def add_simulation_config(self):
        raise NotImplementedError()





