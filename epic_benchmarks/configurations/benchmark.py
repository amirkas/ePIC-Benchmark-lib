import uuid
from dataclasses import dataclass, fields, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Self, Union

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

from epic_benchmarks.configurations._config import ConfigurationModel
from epic_benchmarks.configurations.detector import DetectorConfig
from epic_benchmarks.configurations.simulation import SimulationConfig
from epic_benchmarks.configurations.utils.equality import any_identical_objects

class BenchmarkConfig(ConfigurationModel):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, init=False)
    name : Optional[str] = Field(default=None)
    epic_branch : str
    detector_configs : List[DetectorConfig] = Field(default_factory=list)
    simulation_configs : List[SimulationConfig] = Field(default_factory=list)
    benchmark_dir_name: Optional[str] = Field(default=None)
    epic_directory_name : str = Field(default="epic")
    simulation_out_directory_name : str = Field(default="simulations")
    reconstruction_out_directory_name : str = Field(default="reconstructions")
    analysis_out_directory_name : str = Field(default="analysis")
    simulation_temp_directory_name : str = Field(default="simulations_temp", init=False)
    reconstruction_temp_directory_name : str = Field(default="reconstructions_temp", init=False)


    @field_validator('name', mode='after')
    def validate_name(cls, v : Any, info : ValidationInfo) -> str:

        if v is None:
            config_uuid = info.data["id"]
            return f"Benchmark_{config_uuid}"

        return v

    @field_validator('epic_branch', mode='after')
    def check_epic_branch_exists(cls, v : Any) -> str:

        #TODO: Check branches from epic repository and check if self.epic_branch is valid
        return v

    @field_validator('benchmark_dir_name', mode='after')
    def validate_benchmark_dir(cls, v : Any, info : ValidationInfo) -> str:

        if v is None:
            config_name = info.data["name"]
            return config_name
        return v

    @field_validator('simulation_temp_directory_name',mode='before')
    def define_temp_sim_dir(cls, v : Any, info : ValidationInfo) -> str:
        sim_out_dir = info.data["simulation_out_directory_name"]
        return f"{sim_out_dir}_temp"


    @field_validator('reconstruction_temp_directory_name', mode='before')
    def define_temp_recon_dir(cls, v : Any, info : ValidationInfo) -> str:
        recon_out_dir = info.data["reconstruction_out_directory_name"]
        return f"{recon_out_dir}_temp"

    @model_validator(mode='after')
    def validate_unique_simulations(self) -> Self:

        if any_identical_objects(self.simulation_configs):
            raise AttributeError("All simulation configurations must be unique")
        return self

    @model_validator(mode='after')
    def validate_unique_detector_configs(self) -> Self:

        if any_identical_objects(self.detector_configs):
            raise AttributeError("All detector configurations must be unique")
        return self

    @model_validator(mode='after')
    def validate_unique_directories(self) -> Self:

        directories_to_check = [
            self.epic_directory_name,
            self.simulation_out_directory_name,
            self.reconstruction_out_directory_name,
            self.analysis_out_directory_name,
            self.simulation_temp_directory_name,
            self.reconstruction_temp_directory_name
        ]
        if any_identical_objects(directories_to_check):
            raise AttributeError("All benchmark subdirectory names must be unique")
        return self


    def add_simulation_config(self, simulation_config: SimulationConfig) -> None:
        self.simulation_configs.append(simulation_config)

    def add_detector_config(self, detector_config: DetectorConfig) -> None:
        self.detector_configs.append(detector_config)

    def get_simulation_config(self, simulation_name : str) -> SimulationConfig:

        for simulation in self.simulations:
            if simulation.name == simulation_name:
                return simulation
        err = f"Simulation config with name '{simulation_name}' not found"
        raise ValueError(err)

    def npsim_command_str(self, simulation_name : str) -> str:

        raise NotImplementedError()

    def eicrecon_command_str(self, simulation_name : str) -> str:

        raise NotImplementedError()

    def apply_detector_configs(self, working_dir : Union[str, Path]):

        for detector_config in self.detector_configs:
            epic_dir = self.epic_repo_path(working_dir)
            detector_config.apply_changes(directory_path=epic_dir)

    def simulation_names(self):
        names = []
        for simulation in self.simulations:
            names.append(simulation.name)
        return names

    def benchmark_dir_path(self, working_dir : Union[str, Path]) -> Path:

        if isinstance(working_dir, str):
            working_dir = Path(working_dir)
        return working_dir.joinpath(self.benchmark_dir_name)

    def epic_repo_path(self, working_dir : Union[str, Path]) -> Path:

        _benchmark_dir_path = self.benchmark_dir_path(working_dir)
        return _benchmark_dir_path.joinpath(self.epic_directory_name)

    def simulation_out_dir_path(self, working_dir : Union[str, Path]) -> Path:

        _benchmark_dir_path = self.benchmark_dir_path(working_dir)
        return _benchmark_dir_path.joinpath(self.simulation_out_directory_name)

    def reconstruction_out_dir_path(self, working_dir : Union[str, Path]) -> Path:
        _benchmark_dir_path = self.benchmark_dir_path(working_dir)
        return _benchmark_dir_path.joinpath(self.reconstruction_out_directory_name)

    def analysis_out_dir_path(self, working_dir : Union[str, Path]) -> Path:
        _benchmark_dir_path = self.benchmark_dir_path(working_dir)
        return _benchmark_dir_path.joinpath(self.analysis_out_directory_name)

    def simulation_out_file_path(self, simulation_name : str, working_dir : Union[str, Path]) -> Path:
        simulation_config = self.get_simulation_config(simulation_name)
        npsim_filename = simulation_config.npsim_filename
        simulation_out_dir = self.simulation_out_dir_path(working_dir)
        return simulation_out_dir.joinpath(npsim_filename)

    def reconstruction_out_file_path(self, simulation_name : str, working_dir : Union[str, Path]) -> Path:
        simulation_config = self.get_simulation_config(simulation_name)
        eicrecon_filename = simulation_config.eicrecon_filename
        reconstruction_out_dir = self.reconstruction_out_dir_path(working_dir)
        return reconstruction_out_dir.joinpath(eicrecon_filename)

    def simulation_temp_dir_path(self, working_dir : Union[str, Path]) -> Path:
        _benchmark_dir_path = self.benchmark_dir_path(working_dir)
        return _benchmark_dir_path.joinpath(self.simulation_temp_directory_name)

    def reconstruction_temp_dir_path(self, working_dir : Union[str, Path]) -> Path:
        _benchmark_dir_path = self.benchmark_dir_path(working_dir)
        return _benchmark_dir_path.joinpath(self.reconstruction_temp_directory_name)

    def detector_build_path(self, simulation_name : str, working_dir : Union[str, Path]) -> Path:
        simulation_config = self.get_simulation_config(simulation_name)
        detector_relative_path = simulation_config.detector_relative_path
        epic_path = self.epic_repo_path(working_dir)
        return epic_path.joinpath(detector_relative_path)

    def npsim_cmd(self, simulation_name : str, working_dir : Union[str, Path]) -> str:
        simulation_config = self.get_simulation_config(simulation_name)
        epic_path = self.epic_repo_path(working_dir)
        simulation_out_dir = self.simulation_out_dir_path(working_dir)
        npsim_cmd_str = simulation_config.npsim_cmd(
            epic_repo_path=epic_path,
            output_dir_path=simulation_out_dir
        )
        return npsim_cmd_str

    def eicrecon_cmd(self, simulation_name : str, working_dir : Union[str, Path]) -> str:
        simulation_config = self.get_simulation_config(simulation_name)
        epic_path = self.epic_repo_path(working_dir)
        simulation_out_dir = self.simulation_out_dir_path(working_dir)
        reconstruction_out_dir = self.reconstruction_out_dir_path(working_dir)
        eicrecon_cmd_str = simulation_config.eicrecon_cmd(
            epic_repo_path=epic_path,
            input_dir_path=simulation_out_dir,
            output_dir_path=reconstruction_out_dir
        )
        return eicrecon_cmd_str

test_simulation = SimulationConfig(
    num_events=100,
    momentum=1000,
    detector_path="D:/Downloads/test.txt",
    distribution_min=99,
    distribution_max=360,
)

# test_benchmark = BenchmarkConfig(
#     epic_branch="main",
#     simulation_configs=[test_simulation]
# )
#
# print(test_benchmark.model_dump(exclude_none=True, exclude=set(["theta_min", "theta_max", "eta_min", "eta_max"])))
# print(repr(test_benchmark))


#
# @dataclass
# class TestBenchmarkConfig(BaseConfig):
#     epic_branch: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="epic_branch",
#         types=[str],
#         default="main",
#         optional=True,
#     ))
#     detector_configs: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="detector_configs",
#         types=Optional[List[Dict[str, Any] | DetectorConfig]],
#         optional=True,
#         nested_config=DetectorConfig
#     ))
#     common_simulation_config: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="common_simulation_config",
#         types=Optional[Dict[str, Any] | CommonSimulationConfig],
#         optional=False,
#         nested_config=CommonSimulationConfig
#     ))
#     simulation_configurations: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="simulation_configurations",
#         types=Optional[List[Dict[str, Any] | SimulationConfig]],
#         default=[],
#         optional=True,
#         nested_config=SimulationConfig
#     ))
#
#     def set_common_simulation_config(self):
#         raise NotImplementedError()
#
#     def add_detector_config(self):
#         raise NotImplementedError()
#
#     def add_simulation_config(self):
#         raise NotImplementedError()
#
#
#
#
#
