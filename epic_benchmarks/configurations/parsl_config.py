import os
import re
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import Optional, Any, List, Dict, Type, Union, TypeVar
from epic_benchmarks.configurations._validators import directory_exists, is_directory_path_writeable

from parsl.config import Config
from pydantic import Field, field_validator, computed_field, BaseModel, ConfigDict, field_serializer

from epic_benchmarks.configurations._config import BaseConfig, ConfigKey, ConfigurationModel
from epic_benchmarks.configurations._parsl.systems import SystemNode
from epic_benchmarks.configurations._parsl.walltime_utils import format_walltime, to_hours

class CpuAffinity(Enum):

    BLOCK = "block"
    ALTERNATING = "alternating"
    BLOCK_REVERSE = "block_reverse"


@dataclass
class QOSProperties(frozen=True):

    QoS: str = field(default='default QoS', init=True)
    max_nodes: float = field(default=1.0, init=True)
    max_time_hours: float = field(default=24, init=True)
    available_cpu_cores: int = field(default=1, init=True)
    submit_limit: int = field(default=1, init=True)
    exclusive : bool = field(default=False, init=True)
    run_limit: Optional[int] = field(default=None, init=True)
    priority: Optional[Any] = field(default=None, init=True)

    min_time_hours: Optional[int] = field(default=0, init=True)

    def validate(self, hours, minutes, seconds, cpu_cores=1, submits=1, runs=1):

        if hours < 0 or minutes < 0 or seconds < 0:
            raise ValueError("hours, minutes, and seconds must be non-negative")

        if cpu_cores <= 0:
            raise ValueError("cpu_cores must be larger than 0")

        if submits <= 0:
            raise ValueError("submits must be larger than 0")

        if runs < 0:
            raise ValueError("runs must be larger than or equal to 0")

        total_hours = to_hours(hours, minutes, seconds)

        if total_hours > self.max_time_hours:
            err = (f"Requested walltime '{format_walltime(hours, minutes, seconds)}'"
                   f" exceeds the maximum walltime for Quality of Service '{self.QoS}'."
                   f" Maximum walltime: {format_walltime(self.max_time_hours, 0, 0)}")
            raise ValueError(err)

        if cpu_cores > self.available_cpu_cores * self.max_nodes:
            err = (f"Requested CPU cores '{cpu_cores}' exceeds available"
                   f" cpu cores for Quality of Service '{self.QoS}'."
                   f"\nAvailable CPU Cores: {self.available_cpu_cores}"
                   )
            raise ValueError(err)
        if submits > self.submit_limit:
            err = (f"Requested submit limit '{submits}' exceeds the maximum submit limit"
                   f" for Quality of Service '{self.QoS}'."
                   f"\nSubmit limit: {self.submit_limit}"
                   )
            raise ValueError(err)

    def validate_resources(self, num_tasks_per_node : int, cores_per_task : int):

        total_cores_per_node = num_tasks_per_node * cores_per_task
        if total_cores_per_node > self.available_cpu_cores:

            err = (f"Requested CPU Cores '{total_cores_per_node}' exceeds available"
                   f" cores for Quality of Service '{self.QoS}'. "
                   f"Available CPU Cores: {self.available_cpu_cores}"
            )
            raise ValueError(err)


class ProviderConfig(BaseModel):

    label : str = field(default="Parsl Provider", init=True)
    parsl_provider_type : Optional[TypeVar] = field(default=None, init=False)

    def to_provider_object(self) -> TypeVar:
        #Must be defined by inherited class
        raise NotImplementedError()





class ExecutorConfig(BaseModel):

    executor_type : TypeVar = Field(default=None, init=False)
    label : Optional[str] = Field(default="Parsl Executor", init=True)
    provider : ProviderConfig = Field(init=True)
    cores_per_worker : float = Field(default=1.0, init=True, gt=0)
    max_workers_per_node : int = Field(default=1, init=True, ge=0)
    cpu_affinity : Optional[CpuAffinity] = Field(default=None, init=True)
    qos : Optional[QOSProperties] = Field(default=None, init=True)
    compute_node : Optional[SystemNode] = Field(default=None, init=True)



    @field_validator("provider", mode='before')
    def validate_provider(cls, value : Any) -> ProviderConfig:

        if isinstance(value, dict):
            return ProviderConfig(**value)
        elif isinstance(value, ProviderConfig):
            return value
        else:
            raise ValueError("'provider' could not be converted to a ProviderConfig")

    @field_serializer('provider')
    def serialize_provider(self, provider : ProviderConfig) -> Any:
        return provider.to_provider_object()

    @computed_field
    @cached_property
    def max_cores_per_node(self) -> float:
        return self.cores_per_worker * self.max_workers_per_node

    def to_executor_object(self):

        executor_params = {}
        all_fields = self.model_fields
        for field_name, field_info in all_fields.items():

            if field_name == "executor_type":
                continue

            field_val = getattr(self, field_name, None)
            if field_val:
                executor_params[field_name] = field_val

        return self.executor_type(**executor_params)



@dataclass
class TestExecutorConfig(BaseConfig):

    _executor_type : Type = field(default=None, init=False)
    label : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="label",
        types=str,
        default="Parsl Executor Config",
        optional=True,
    ))
    provider: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="provider",
        types=[Optional[List[Dict[str, Any]]], Optional[ProviderConfig]],
        default="Parsl Executor Config",
        optional=True,
    ))
    provider: Optional[ProviderConfig] = field(default=None, init=True)
    cores_per_worker: float = field(default=1, init=True)
    max_workers_per_node : int = field(default=None, init=True)
    cpu_affinity : Optional[CpuAffinity] = field(default=None, init=True)
    qos : Optional[QOSProperties] = field(default=None, init=True)
    compute_node : Optional[SystemNode] = field(default=None, init=True)

    def __post_init__(self):

        # Validate that settings are compatible with
        # requested Provider, QOS, Compute Node if provided.
        if not self.provider:
            raise ValueError("Provider must be set")
        else:
            self._validate_provider()
        if self.qos:
            self._validate_qos()
        if self.compute_node:
            self._validate_compute_node()

        #Validation using overridden validate method
        self.validate()

    def validate(self):
        #Any extra validation beyond QoS or Compute Node validation must be implemented by inherited class
        pass

    def to_executor_object(self) -> _executor_type:
        #Must be defined by inherited class
        raise NotImplementedError()


    def _validate_provider(self):
        assert self.provider is not None
        self.provider.validate()

    def _validate_qos(self):

        assert self.qos is not None
        # assert isinstance(self.qos, QOSProperties)
        self.qos.validate_resources(self.max_workers_per_node. self.cores_per_worker)

    def _validate_compute_node(self):

        assert self.compute_node is not None
        self.compute_node.validate_cpu_request(self._max_cores_per_node())

    def _max_cores_per_node(self):

        return self.max_workers_per_node * self.cores_per_worker


class ParslConfig(ConfigurationModel):
    strategy : str = Field(default=None, init=True)
    run_directory : str = Field(default=os.getcwd(), init=True)
    executors : [List[Union[Dict[str, Any], ExecutorConfig]]] = Field(init=True)
    parsl_config : Optional[Config] = Field(default=None, init=False)

    @field_validator('strategy', mode='after')
    def validate_strategy(cls, value : Any) -> Optional[str]:
        if value:
            #TODO: Check if strategy is valid parsl config strategy
            pass
        return value

    @field_validator('run_directory', mode='after')
    def run_directory_exists(cls, value : Any) -> Union[str, None]:

        if value:
            if not directory_exists(value):
                err = f"Directory '{value}' does not exists"
                raise ValueError(err)
            if not is_directory_path_writeable(value):
                err = f"Directory '{value}' is not writable"
                raise ValueError(err)
        return value

    @field_validator('executor_configs', mode='before')
    def validate_executor_configs(cls, value : Any) -> List[ExecutorConfig]:
        if len(value) == 0:
            raise ValueError("At least one executor_config is required")
        parsed_list = []
        for exec_config in value:
            if isinstance(exec_config, dict):
                as_executor_config = ExecutorConfig(**exec_config)
                parsed_list.append(as_executor_config)
            else:
                parsed_list.append(exec_config)
        return parsed_list

    @field_serializer('executors')
    def serialize_executors(self, executors : List[Union[Dict[str, Any], ExecutorConfig]]) -> List[Any]:
        serialized_executors = []
        for executor in executors:
            serialized_executors.append(executor.to_provider_object())
        return serialized_executors

    def to_parsl_config_object(self) -> Config:
        model_dict = self.model_dump()
        return Config(**model_dict)



@dataclass
class TestParslConfig(BaseConfig):

    _parsl_config : Optional[Config] = field(default=None, init=False)
    strategy : ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="strategy",
        types=str,
        default=None,
        optional=True,
    ))
    run_dir: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="run_dir",
        types=str,
        default=None,
        optional=True,
    ))
    executor_configs: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="run_dir",
        types=Optional[List[Dict[str, Any] | ExecutorConfig]],
        default=None,
        optional=True,
        nested_config=ExecutorConfig
    ))

    def to_parsl_config(self) -> Config:

        assert self.executor_configs is not None

        _executor_objs = [_executor.to_executor_object() for _executor in self.executor_configs]
        _strategy = self.strategy
        _run_dir = self.run_dir

        params = {
            "executors" : _executor_objs,
            "strategy" : _strategy,
            "run_dir" : _run_dir,
        }
        params = filter(lambda x, y : y is not None, params)
        return Config(**params)

    def validate(self):

        if self.executor_configs is None:
            err = f"At least one executor must be provided"
            raise ValueError(err)
        #TODO: Add validation for valid parsl strategies
        #TODO: Add validation for run directory


    def __post_init__(self):

        self.validate()