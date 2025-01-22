from __future__ import annotations
from doctest import script_from_examples
from functools import cached_property
import os
from pathlib import Path
from typing import Optional, List, Any, Self

from parsl import Config
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator, ConfigDict, FilePath
from pydantic_core.core_schema import ValidationInfo

from epic_benchmarks.parsl.config import ParslConfig
from epic_benchmarks.benchmark.config import BenchmarkConfig
from epic_benchmarks.simulation.config import SimulationConfig
from epic_benchmarks.detector.config import DetectorConfig
from epic_benchmarks._file.types import PathType
from epic_benchmarks._file.utils import save_raw_config, load_from_file
from epic_benchmarks.utils.equality import any_identical_objects

RUN_INFO_DIR_NAME = "runinfo"

class WorkflowConfig(BaseModel):

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True, validate_default=True)

    name : Optional[str] = Field(default="Workflow")
    working_directory : str = Field(default_factory=os.getcwd, init=False)
    workflow_dir_name : Optional[str] = Field(default="Benchmarks")
    benchmarks : List[BenchmarkConfig] = Field(default_factory=list)
    parsl_config : Optional[ParslConfig] = Field(default=None)
    script_path : Optional[PathType] = Field(default=None)
    debug : bool = Field(default=False)
    redo_all_benchmarks : bool = Field(default=False)
    redo_all_benchmarks : bool = Field(default=False)
    keep_epic_repos : bool = Field(default=False)
    keep_simulation_outputs : bool = Field(default=False)
    keep_reconstruction_outputs : bool = Field(default=False)

    @cached_property
    def paths(self):
        from epic_benchmarks.workflow._inner import WorkflowPaths
        return WorkflowPaths(parent=self)
    
    @cached_property
    def executor(self):
        from epic_benchmarks.workflow._inner import WorkflowExecutor
        return WorkflowExecutor(parent=self)

    def add_benchmark(self, benchmark_config : BenchmarkConfig) -> None:
        self.benchmarks.append(benchmark_config)

    @classmethod
    def load_from_file(cls, filepath) -> WorkflowConfig:

        loaded_data = load_from_file(filepath)
        suite_config = WorkflowConfig.model_validate(loaded_data)
        return suite_config

    @classmethod
    def save_to_file(cls, filepath : PathType, suite_config : WorkflowConfig) -> None:

        save_raw_config(raw_config=suite_config, file_path=filepath, overwrite=True)

    def save(self, filepath : PathType):

        WorkflowConfig.save_to_file(filepath, self)

    @cached_property
    def workflow_dir_path(self):

        working_dir_path = Path(self.working_directory).resolve()
        return working_dir_path.joinpath(self.workflow_dir_name).resolve()

    def benchmark_names(self):

        names = []
        for benchmark in self.benchmarks:
            names.append(benchmark.name)
        return names

    def benchmark_config(self, benchmark_name : str) -> BenchmarkConfig:

        for benchmark in self.benchmarks:
            if benchmark.name == benchmark_name:
                return benchmark

        err = f"Benchmark config with name '{benchmark_name}' could be found"
        raise ValueError(err)

    def simulation_names(self, benchmark_name : str):
        benchmark_config = self.benchmark_config(benchmark_name)
        return benchmark_config.simulation_names()

    def simulation_config(self, benchmark_name : str, simulation_name : str) -> SimulationConfig:

        benchmark_config = self.benchmark_config(benchmark_name)
        return benchmark_config.get_simulation_config(simulation_name)
        
    @field_validator('parsl_config', mode='before')
    def validate_parsl_config(cls, value : Any, info : ValidationInfo) -> ParslConfig:
        if value is None:
            raise ValueError("Parsl configuration must be provided")
        if isinstance(value, ParslConfig):
            return value
        elif isinstance(value, dict):
            try:
                return ParslConfig(**value)
            except Exception as e:
                raise e
        elif isinstance(value, Config):
            return ParslConfig.model_validate(value)
        else:
            raise ValueError("Could not parse parsl configuration")
        
    @field_validator('parsl_config', mode='after')
    def update_parsl_directories(cls, parsl_config : ParslConfig, info : ValidationInfo) -> ParslConfig:

        working_dir = Path(info.data["working_directory"]).resolve()
        workflow_dir_name = info.data["workflow_dir_name"]
        run_dir = working_dir.joinpath(workflow_dir_name, RUN_INFO_DIR_NAME).resolve()
        parsl_config.run_dir = str(run_dir)
        # for executor in parsl_config.executors:
        #     executor.working_dir = str(run_dir)
        return parsl_config
    
    @field_validator('script_path', mode='after')
    def check_script_exists(cls, script_path : PathType, info : ValidationInfo) -> str:

        if script_path is None:
            return script_path
        elif isinstance(script_path, str):
           script_path = Path(script_path)
        #If given path doesn't exist. Attempt to join it with the CWD to produce an absolute path 
        if not script_path.exists():
            cwd = Path(info.data['working_directory']).resolve()
            script_path = cwd.joinpath(script_path)
            #If joined path still doesn't exist, raise validation error.
            if not script_path.exists():
                err = f"Path to workflow script '{script_path}' does not exist."
                raise ValidationError(err)
        return str(script_path)
    
    @model_validator(mode='after')
    def validate_unique_benchmarks(self) -> Self:

        if any_identical_objects(self.benchmarks):
            raise AttributeError("All benchmarks must be unique")
        return self
