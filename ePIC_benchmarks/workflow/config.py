from __future__ import annotations
from functools import cached_property
import os
from pathlib import Path
from typing import Optional, List, Any, Self, Callable

from parsl import Config
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator, ConfigDict, AliasChoices
from pydantic_core.core_schema import ValidationInfo

from ePIC_benchmarks.parsl.config import ParslConfig
from ePIC_benchmarks.benchmark.config import BenchmarkConfig
from ePIC_benchmarks.simulation.config import SimulationConfig
from ePIC_benchmarks.detector.config import DetectorConfig
from ePIC_benchmarks.parsl.executors import HighThroughputExecutorConfig, MPIExecutorConfig, WorkQueueExecutorConfig
from ePIC_benchmarks.workflow.future import WorkflowFuture
from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks._file.utils import save_raw_config, load_from_file
from ePIC_benchmarks.utils.equality import any_identical_objects
from ePIC_benchmarks._file.supported import DEFAULT_CONFIG_FILE_EXT

RUN_INFO_DIR_NAME = "runinfo"

class WorkflowConfig(BaseModel):

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True, validate_default=True)

    name : Optional[str] = Field(
        default="Workflow",
        description="Name of the ePIC Simulation Workflow",
        validation_alias=AliasChoices(
            "name",
            "workflow_dir_name",
            "workflow_name"
        )
    )
    debug : bool = Field(
        default=False,
        description="Toggle whether debugging output is saved to the filesystem"
    )
    working_directory : str = Field(
        default_factory=os.getcwd,
        init=False,
        exclude=True,
        description="Path to the current working directory"
    )
    benchmarks : List[BenchmarkConfig] = Field(default_factory=list)
    redo_all_benchmarks : bool = Field(default=False)
    redo_epic_building : bool = Field(default=False)
    redo_simulations : bool = Field(default=False)
    redo_reconstructions : bool = Field(default=False)
    redo_analysis : bool = Field(default=False)
    parsl_config : Optional[ParslConfig] = Field(default=None)
    script_path : Optional[PathType] = Field(default=None, deprecated=True)
    workflow_script : Optional[Callable[[Self], WorkflowFuture]] = Field(default=None, exclude=True)
    keep_epic_repos : bool = Field(default=True)
    keep_simulation_outputs : bool = Field(default=True)
    keep_reconstruction_outputs : bool = Field(default=True)
    keep_analysis_outputs : bool = Field(default=True)

    @cached_property
    def paths(self):
        from ._inner.paths import WorkflowPaths
        return WorkflowPaths(parent=self)
    
    @cached_property
    def executor(self):
        from ._inner.executor import WorkflowExecutor
        return WorkflowExecutor(parent=self)

    def add_benchmark(self, benchmark_config : BenchmarkConfig) -> None:
        self.benchmarks.append(benchmark_config)

    @classmethod
    def load_from_file(cls, filepath) -> WorkflowConfig:

        loaded_data = load_from_file(filepath)
        suite_config = WorkflowConfig.model_validate(loaded_data)
        return suite_config

    #Saves workflow config to file
    @classmethod
    def save_to_file(cls, suite_config : WorkflowConfig, filepath : Optional[PathType] = None) -> None:

        suite_config.save(filepath=filepath)

    def save(self, filepath : Optional[PathType] = None):

        if filepath is None:
            working_directory = Path(self.working_directory).resolve()
            filename = f'{self.name}_config{DEFAULT_CONFIG_FILE_EXT}'
            filepath = working_directory.joinpath(working_directory, filename)
            
        save_raw_config(raw_config=self, file_path=filepath, overwrite=True)

    @cached_property
    def workflow_dir_path(self):

        working_dir_path = Path(self.working_directory).resolve()
        return working_dir_path.joinpath(self.name).resolve()

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
    def update_parsl_run_dir(cls, parsl_config : ParslConfig, info : ValidationInfo) -> ParslConfig:

        working_dir = Path(info.data["working_directory"])
        workflow_dir_name = info.data["name"]
        run_dir = working_dir.joinpath(workflow_dir_name, RUN_INFO_DIR_NAME)
        parsl_config.run_dir = str(run_dir)
        return parsl_config
    
    # @field_validator('parsl_config', mode='after')
    # def init_monitoring_database(cls, parsl_config : ParslConfig, info : ValidationInfo) -> ParslConfig:

    #     if parsl_config.monitoring is not None:
    #         parsl_run_dir = parsl_config.run_dir
    #         db_path = os.path.join(parsl_run_dir, "monitoring.db")
    #         conn = sqlite3.connect(db_path)
    #         conn.close()
    #     return parsl_config

    
    @field_validator('parsl_config', mode='after')
    def update_parsl_debug_mode(cls, parsl_config : ParslConfig, info : ValidationInfo) -> ParslConfig:

        working_dir = Path(info.data["working_directory"])
        workflow_dir_name = info.data["name"]
        debug_enabled = info.data["debug"]

        parsl_config.initialize_logging = debug_enabled
        for executor in parsl_config.executors:
            executor.working_dir = str(working_dir.joinpath(workflow_dir_name))
            if isinstance(executor, (HighThroughputExecutorConfig, MPIExecutorConfig)):
                executor.worker_debug = debug_enabled
            elif isinstance(executor, WorkQueueExecutorConfig):
                executor.full_debug = debug_enabled
        
        return parsl_config

        
    @field_validator('parsl_config', mode='after')
    def update_parsl_checkpointing_mode(cls, parsl_config : ParslConfig, info : ValidationInfo) -> ParslConfig:

        enable_checkpointing = not info.data['redo_all_benchmarks']
        if enable_checkpointing:
            parsl_config.checkpoint_mode = 'task_exit'
        
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
