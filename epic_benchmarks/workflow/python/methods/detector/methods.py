from pathlib import Path

from epic_benchmarks.workflow.config import WorkflowConfig

def apply_detector_configs(benchmark_suite_config : WorkflowConfig, benchmark_name : str, **kwargs) -> None:

    benchmark_suite_config.executor.apply_detector_configs(benchmark_name=benchmark_name)