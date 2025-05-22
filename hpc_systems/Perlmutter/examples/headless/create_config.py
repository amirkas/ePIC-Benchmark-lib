from ePIC_benchmarks.workflow import WorkflowConfig
from ePIC_benchmarks.benchmark import BenchmarkConfig
from ePIC_benchmarks.simulation import SimulationConfig
from ePIC_benchmarks.detector import DetectorConfig
from ePIC_benchmarks.detector.xml_elements.detector import (
    XmlDetectorElement, XmlModuleElement, XmlModuleComponentElement
)
from ePIC_benchmarks.parsl.config import ParslConfig
from ePIC_benchmarks.parsl.executors import HighThroughputExecutorConfig
from ePIC_benchmarks.parsl.providers import LocalProviderConfig
from ePIC_benchmarks.parsl.launchers import SrunLauncherConfig
import numpy as np


MOMENTA = [0.5, 1, 2, 5, 10, 15]
ETA_RANGES = []
simulation_configs = []

