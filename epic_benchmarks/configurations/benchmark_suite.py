from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Self

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

from epic_benchmarks.configurations.parsl_config import ParslConfig
from epic_benchmarks.configurations._config import ConfigurationModel
from epic_benchmarks.configurations.benchmark import BenchmarkConfig
from epic_benchmarks.configurations.utils.file_utils import save_raw_config, load_from_file
from epic_benchmarks.configurations.utils.equality import any_identical_objects
from epic_benchmarks.configurations import DEFAULT_CONFIG_FILE_EXT, SimulationConfig


class BenchmarkSuiteConfig(ConfigurationModel):

    name : Optional[str] = Field(default="Benchmark Suite")
    benchmarks : List[BenchmarkConfig] = field(default_factory=list)
    parsl_config : Optional[ParslConfig] = field(default=None)
    benchmark_suite_dir_name : Optional[str] = Field(default="Benchmarks")
    save_filepath: Optional[str] = Field(default=None)

    @field_validator('save_filepath')
    def format_save_filepath(cls, v : Any, info : ValidationInfo):

        if v is None:
            config_name = info.data["name"].replace(" ", "_")
            cwd = os.getcwd()
            default_extension = DEFAULT_CONFIG_FILE_EXT
            file_name = f"{config_name}{default_extension}"
            save_filepath = os.path.join(cwd, file_name)
            return save_filepath
        return v

    @model_validator(mode='after')
    def validate_unique_benchmarks(self) -> Self:

        if any_identical_objects(self.benchmarks):
            raise AttributeError("All benchmarks must be unique")
        return self

    def add_benchmark(self, benchmark_config : BenchmarkConfig) -> None:
        self.benchmarks.append(benchmark_config)

    @classmethod
    def load_from_file(cls, filepath) -> BenchmarkSuiteConfig:

        loaded_data = load_from_file(filepath)
        suite_config = BenchmarkSuiteConfig.model_validate(loaded_data)
        return suite_config

    @classmethod
    def save_to_file(cls, filepath : str, suite_config : BenchmarkSuiteConfig) -> None:

        save_raw_config(raw_config=suite_config, file_path=filepath)

    def save(self):

        BenchmarkSuiteConfig.save_to_file(self.save_filepath, self)


    def benchmark_names(self):

        names = []
        for benchmark in self.benchmarks:
            names.append(benchmark.name)
        return names

    def get_benchmark_config(self, benchmark_name : str) -> BenchmarkConfig:

        for benchmark in self.benchmarks:
            if benchmark.name == benchmark_name:
                return benchmark

        err = f"Benchmark config with name '{benchmark_name}' could be found"
        raise ValueError(err)

    def simulation_names(self, benchmark_name : str):
        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.simulation_names()

    def get_simulation_config(self, benchmark_name : str, simulation_name : str) -> SimulationConfig:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.get_simulation_config(simulation_name)


    def npsim_command_str(self, benchmark_name : str, simulation_name : str) -> str:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.npsim_command_str(simulation_name)

    def eicrecon_command_str(self, benchmark_name : str,  simulation_name : str) -> str:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.eicrecon_command_str(simulation_name)

    def apply_detector_configs(self, benchmark_name : str, working_dir : Union[str, Path]):

        benchmark_config = self.get_benchmark_config(benchmark_name)
        benchmark_config.apply_detector_configs(working_dir)

    def benchmark_dir_path(self, benchmark_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.benchmark_dir_path(working_dir)

    def epic_repo_path(self, benchmark_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.epic_repo_path(working_dir)


    def simulation_out_dir_path(self, benchmark_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.simulation_out_dir_path(working_dir)

    def reconstruction_out_dir_path(self, benchmark_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.reconstruction_out_dir_path(working_dir)

    def analysis_out_dir_path(self, benchmark_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.analysis_out_dir_path(working_dir)

    def simulation_out_file_path(self, benchmark_name : str, simulation_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.simulation_out_file_path(simulation_name, working_dir)

    def reconstruction_out_file_path(self, benchmark_name : str, simulation_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.reconstruction_out_file_path(simulation_name, working_dir)

    def simulation_temp_dir_path(self, benchmark_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.simulation_temp_dir_path(working_dir)

    def reconstruction_temp_dir_path(self, benchmark_name : str, working_dir : Union[str, Path]) -> Path:

        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.reconstruction_temp_dir_path(working_dir)

    def detector_build_path(self, benchmark_name : str, simulation_name : str, working_dir : Union[str, Path]) -> Path:
        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.detector_build_path(simulation_name, working_dir)


    def npsim_cmd(self, benchmark_name : str, simulation_name : str, working_dir : Union[str, Path]) -> str:
        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.npsim_cmd(simulation_name, working_dir)

    def eicrecon_cmd(self, benchmark_name : str, simulation_name : str, working_dir : Union[str, Path]) -> str:
        benchmark_config = self.get_benchmark_config(benchmark_name)
        return benchmark_config.eicrecon_cmd(simulation_name, working_dir)



#
# @dataclass
# class TestBenchmarkSuiteConfig(BaseConfig):
#
#     save_filepath : Optional[str] = field(init=True, default=None)
#     save_dir: Optional[str] = field(init=True, default=None)
#
#     name: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="name",
#         types=str,
#         default="Benchmark_Suite",
#         optional=True,
#     ))
#     benchmarks: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="benchmarks",
#         types=Optional[List[Dict[str, Any] | BenchmarkConfig]],
#         optional=True,
#         nested_config=BenchmarkConfig
#     ))
#     parsl_config: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="parsl_config",
#         types=Optional[List[Dict[str, Any] | ParslConfig]],
#         optional=True,
#         nested_config=ParslConfig
#     ))
#
#     def add_benchmark(self):
#         raise NotImplementedError()
#
#     def save(self):
#
#         if self.save_filepath is None:
#             raise AttributeError("Must provide a location to save the configuration")
#         _path = self.save_filepath
#
#         if self.save_dir:
#             _path = os.path.join(self.save_dir, _path)
#         _dir = os.path.dirname(_path)
#         #Check if ancestor directory of filepath exists
#         if not os.path.exists(_dir):
#             err = f"Directory {_dir} does not exist. Create the parent directory of the file and try again."
#             raise ValueError(err)
#         #Check if user has write permissions at path
#         if not os.access(_path, os.W_OK):
#             err = f"Path {_path} is not writeable. Check file permissions at the path."
#             raise ValueError(err)
#         #Check if provided file extension is currently supported for configuration.
#         _, ext = os.path.splitext(_path)
#         if ext not in self.SUPPORTED_FILES:
#             err = (f"File extension {ext} is not supported. "
#                    f"Request support for {ext} files by submitting an issue at "
#                    f"'https://github.com/amirkas/ePIC-Benchmark-lib' or add "
#                    f"support yourself and submit a pull request."
#             )
#             raise ValueError(err)
#
#         try:
#             with open(_path, "w") as file:
#                 yaml.safe_dump(self.to_dict(), file)
#         except Exception as e:
#             print(f"Failed to save File at path: '{_path}. Got Exception:\n'", e)