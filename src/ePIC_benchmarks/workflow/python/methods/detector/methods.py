from pathlib import Path
from parsl import AUTO_LOGNAME

from ePIC_benchmarks.workflow.config import WorkflowConfig

#Applies the updates defined by the list 'DetectorConfig's for a BenchmarkConfig
def apply_detector_configs(
        benchmark_suite_config : WorkflowConfig,
        benchmark_name : str,
        stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME,
        **kwargs) -> None:


    benchmark_suite_config.executor.apply_detector_configs(benchmark_name=benchmark_name)
