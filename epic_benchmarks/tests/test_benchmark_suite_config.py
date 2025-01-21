
import unittest
import os

from epic_benchmarks.parsl.config import ParslConfig
from parsl import Config

from epic_benchmarks.simulation.config import SimulationConfig
from epic_benchmarks.benchmark.config import BenchmarkConfig
from epic_benchmarks.workflow.config import WorkflowConfig
from epic_benchmarks.simulation.types import GunDistribution
from epic_benchmarks.parsl.executors import HighThroughputExecutorConfig
from epic_benchmarks.parsl.providers import LocalProviderConfig


TEST_OUTPUT_DIR = "/global/cfs/cdirs/m3763/amir/workspace/benchmarks/lib/epic_benchmarks/tests/out"


DETECTOR_PATH = os.getcwd()
NUM_EVENTS = 10
MOMENTUM = 1000
DISTRIBUTION = GunDistribution.Uniform
DISTRIBUTION_MIN = 0
DISTRIBUTION_MAX = 180

EPIC_BRANCH = "main"



class TestBasicSuiteConfig(unittest.TestCase):


    basic_simulation_config = SimulationConfig(
        detector_relative_path=DETECTOR_PATH,
        num_events=NUM_EVENTS,
        momentum=MOMENTUM,
        type=DISTRIBUTION,
        theta_min=DISTRIBUTION_MIN,
        theta_max=DISTRIBUTION_MAX        
    )

    basic_benchmark_config = BenchmarkConfig(
        epic_branch=EPIC_BRANCH,
        simulation_configs=[basic_simulation_config]
    )

    local_parsl_config = ParslConfig(
            executors=[
                HighThroughputExecutorConfig(
                    label="HTEX_Headless",
                    max_workers_per_node=1,
                    cores_per_worker=1,
                    provider=LocalProviderConfig(
                        nodes_per_block=1,
                        cmd_timeout=120,
                    ),
                ),
            ],
            strategy=None,
    )

    basic_workflow_config = WorkflowConfig(
        benchmarks=[basic_benchmark_config],
        parsl_config=local_parsl_config
    )

    def test_model_created(self):

        print(self.basic_workflow_config.model_dump())
        assert(True)  # add assertion here

    def test_model_save(self):
        output_file = os.path.join(TEST_OUTPUT_DIR, "test_model1.yml")
        self.basic_workflow_config.save(output_file)

        #Cleanup. Delete file if it exists after test completion

    def test_npsim_cmd(self):

        for benchmark_name in self.basic_workflow_config.benchmark_names():
            for simulation_name in self.basic_workflow_config.simulation_names(benchmark_name):
                print(self.basic_workflow_config.executor.npsim_command_string(benchmark_name, simulation_name))

    def test_parsl_config(self):

        print(self.local_parsl_config.model_dump())

        print("Epic benchmarks ParslConfig is a Parsl Config from method: ", isinstance(self.local_parsl_config.to_parsl_config(), Config))
        print(self.local_parsl_config.to_parsl_config())
        # print(self.local_parsl_config.to_parsl_config())
        # print(type(self.local_parsl_config.to_parsl_config()))
        # executors = self.local_parsl_config.executors
        # local_executor = executors[0]
        # print("Epic benchmarks ParslExecutorConfig is a Parsl Executor: ", isinstance(local_executor.to_parsl_config(), ParslExecutor))
        # print("Epic benchmarks ParslProviderConfig is a Parsl ExecutorProvider: ", isinstance(local_executor.provider.to_parsl_config(), ExecutionProvider))

    # def test_workflow_executor_init(self):

    #     basic_benchmark_suite_config_two = BenchmarkSuiteConfig(
    #         benchmarks=[self.basic_benchmark_config],
    #         parsl_config=self.local_parsl_config
    #     )
    #     workflow_executor = WorkflowBase(
    #         benchmark_suite_config=basic_benchmark_suite_config_two
    #     )
    #     print(workflow_executor.__dict__)

    # def test_workflow_executor_run(self):

    #     basic_benchmark_suite_config_three = BenchmarkSuiteConfig(
    #         benchmarks=[self.basic_benchmark_config],
    #         parsl_config=self.local_parsl_config
    #     )
    #     workflow_executor = WorkflowBase(
    #         benchmark_suite_config=basic_benchmark_suite_config_three
    #     )
    #     workflow_executor.run_benchmarks()



if __name__ == '__main__':
    unittest.main()
