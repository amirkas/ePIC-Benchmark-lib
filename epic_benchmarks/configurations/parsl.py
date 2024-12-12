import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, List, Dict, Type

from parsl import Config
from parsl.executors import HighThroughputExecutor
from parsl.providers import LocalProvider
from parsl.channels import LocalChannel

from epic_benchmarks.configurations._config import BaseConfig, ConfigKey
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

@dataclass
class ProviderConfig:

    label : str = field(default="Parsl Provider", init=True)
    _parsl_provider_type : Optional[Any] = field(default=None, init=False)

    def to_provider_object(self) -> _parsl_provider_type:
        #Must be defined by inherited class
        raise NotImplementedError()

    def validate(self, **kwargs):
        #Any validation must be implemented by inherited class
        pass

@dataclass
class ExecutorConfig:

    _executor_type : Type = field(default=None, init=False)
    label : str = field(default="Parsl Executor", init=True)
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


@dataclass
class ParslConfig(BaseConfig):

    _parsl_config : Optional[Config] = field(default=None, init=False)
    strategy : Optional[str] = field(default=None, init=True)
    run_dir : Optional[str] = field(default=None, init=True)
    executor_configs: Optional[List[ExecutorConfig]] = field(default=None, init=True)


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