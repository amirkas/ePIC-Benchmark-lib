from .simulation_config_ex import EXAMPLE_SIMULATION_CONFIG
from .detector_config_ex import EXAMPLE_DETECTOR_CONFIG
from ePIC_benchmarks.benchmark import BenchmarkConfig

EXAMPLE_BENCHMARK_CONFIG = BenchmarkConfig(
    simulation_configs=[EXAMPLE_SIMULATION_CONFIG],
    detector_configs=[EXAMPLE_DETECTOR_CONFIG],
    epic_branch="main",
    generate_material_map=False
)
