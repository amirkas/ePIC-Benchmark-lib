from functools import cached_property
from pathlib import Path
from ePIC_benchmarks.benchmark.config import BenchmarkConfig
from ePIC_benchmarks.simulation.config import SimulationConfig
from ePIC_benchmarks.workflow.config import WorkflowConfig

class WorkflowPaths:

    parent : WorkflowConfig

    def __init__(self, parent):
        assert(isinstance(parent, WorkflowConfig))
        self.parent = parent

    @cached_property
    def workflow_dir_path(self):

        #TODO: Rework required to avoid user defined Dir_name/Same_dir_name bug
        working_dir_path = Path(self.parent.working_directory).resolve()
        if working_dir_path.parts[-1] == self.parent.name:
            return working_dir_path
        return working_dir_path.joinpath(self.parent.name)

    def benchmark_names(self):

        names = []
        for benchmark in self.parent.benchmarks:
            names.append(benchmark.name)
        return names

    def benchmark_config(self, benchmark_name : str) -> BenchmarkConfig:

        for benchmark in self.parent.benchmarks:
            if benchmark.name == benchmark_name:
                return benchmark

        err = f"Benchmark config with name '{benchmark_name}' could be found"
        raise ValueError(err)

    def simulation_names(self, benchmark_name : str):
        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.simulation_names()

    def simulation_config(self, benchmark_name : str, simulation_name : str) -> SimulationConfig:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.get_simulation_config(simulation_name)

    def epic_branch(self, benchmark_name : str) -> str:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.epic_branch

    def apply_detector_configs(self, benchmark_name : str):

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        benchmark_config.apply_detector_configs(self.workflow_dir_path)

    def benchmark_dir_path(self, benchmark_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.benchmark_dir_path(self.workflow_dir_path)

    def epic_repo_path(self, benchmark_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.epic_repo_path(self.workflow_dir_path)
    
    def material_map_dir_path(self, benchmark_name):

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        epic_dir_path = benchmark_config.epic_repo_path(self.workflow_dir_path)
        if benchmark_config.existing_material_map_path is None:
            return epic_dir_path.joinpath("scripts", "material_map")
        else:
            return benchmark_config.existing_material_map_path

    def material_map_script_path(self, benchmark_name):

        material_map_dir = self.material_map_dir_path(benchmark_name)
        return material_map_dir.joinpath("run_material_map_validation.sh")

    def material_map_path(self, benchmark_name : str, file_name : str = "material-map.cbor") -> Path:

        material_map_dir = self.material_map_dir_path(benchmark_name)
        return material_map_dir.joinpath(file_name)

    def simulation_out_dir_path(self, benchmark_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.simulation_out_dir_path(self.workflow_dir_path)

    def reconstruction_out_dir_path(self, benchmark_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.reconstruction_out_dir_path(self.workflow_dir_path)

    def analysis_out_dir_path(self, benchmark_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.analysis_out_dir_path(self.workflow_dir_path)

    def simulation_out_file_path(self, benchmark_name : str, simulation_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.simulation_out_file_path(simulation_name, self.workflow_dir_path)

    def reconstruction_out_file_path(self, benchmark_name : str, simulation_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.reconstruction_out_file_path(simulation_name, self.workflow_dir_path)

    def simulation_temp_dir_path(self, benchmark_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.simulation_temp_dir_path(self.workflow_dir_path)

    def reconstruction_temp_dir_path(self, benchmark_name : str) -> Path:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.reconstruction_temp_dir_path(self.workflow_dir_path)
    
    def simulation_instance_temp_dir_path(self, benchmark_name : str, simulation_name : str) -> Path:

        simulation_temp_path = self.simulation_temp_dir_path(benchmark_name)
        return simulation_temp_path.joinpath(simulation_name)

    def reconstruction_instance_temp_dir_path(self, benchmark_name : str, simulation_name : str) -> Path:
        reconstruction_temp_path = self.reconstruction_temp_dir_path(benchmark_name)
        return reconstruction_temp_path.joinpath(simulation_name)

    def detector_build_path(self, benchmark_name : str, simulation_name : str) -> Path:
        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.detector_build_path(simulation_name, self.workflow_dir_path)
