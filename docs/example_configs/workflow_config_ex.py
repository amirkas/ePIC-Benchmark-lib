from .benchmark_config_ex import EXAMPLE_BENCHMARK_CONFIG
from .parsl_config_ex import EXAMPLE_PARSL_CONFIG
from ePIC_benchmarks.workflow import WorkflowConfig

EXAMPLE_WORKFLOW_CONFIG = WorkflowConfig(
    name="Example Workflow",
    benchmarks=[EXAMPLE_BENCHMARK_CONFIG],
    parsl_config=EXAMPLE_PARSL_CONFIG
)

