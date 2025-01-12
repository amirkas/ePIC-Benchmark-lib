import unittest
import os
from epic_benchmarks.configurations import SimulationConfig, DetectorConfig, BenchmarkConfig, BenchmarkSuiteConfig, ParslConfig
from epic_benchmarks.configurations.simulation_types import GunDistribution

DETECTOR_PATH = os.getcwd()
NUM_EVENTS = 10
MOMENTUM = 1000
DISTRIBUTION = GunDistribution.Uniform
DISTRIBUTION_MIN = 0
DISTRIBUTION_MAX = 180

EPIC_BRANCH = "main"







class TestBasicSuiteConfig(unittest.TestCase):

    basic_simulation_config = SimulationConfig(
        detector_path=DETECTOR_PATH,
        num_events=NUM_EVENTS,
        momentum=MOMENTUM,
        distribution=DISTRIBUTION,
        distribution_min=DISTRIBUTION_MIN,
        distribution_max=DISTRIBUTION_MAX
    )

    basic_benchmark_config = BenchmarkConfig(
        epic_branch=EPIC_BRANCH,
        simulation_configs=[basic_simulation_config]
    )

    basic_benchmark_suite_config = BenchmarkSuiteConfig(
        benchmarks=[basic_benchmark_config]
    )


    def test_something(self):

        print(self.basic_benchmark_suite_config.model_dump())
        self.assertEqual(True, False)  # add assertion here

if __name__ == '__main__':
    unittest.main()
