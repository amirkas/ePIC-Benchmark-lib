import re
import math
from enum import Enum
from dataclasses import dataclass,field
from typing import Optional, Type, Tuple, Any

from parsl import HighThroughputExecutor
from parsl.providers import SlurmProvider
from parsl.launchers import SrunLauncher

from epic_benchmarks.configurations._parsl.systems import SystemNode, SystemNodeType
from epic_benchmarks.configurations._parsl.walltime_utils import format_walltime, _walltime_str_to_tuple
from epic_benchmarks.configurations.parsl import QOSProperties, ProviderConfig, ExecutorConfig


class SlurmPriority(Enum):

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


#Supported Slurm 'Quality of Service's for benchmark workflow
class SlurmQOS(Enum):

    DEBUG = QOSProperties(
        QoS='debug',
        max_nodes=8,
        max_time_hours=0.5,
        exclusive=True,
        available_cpu_cores=64,
        submit_limit=5,
        run_limit=2,
        priority=SlurmPriority.MEDIUM,
    )
    REGULAR = QOSProperties(
        QoS='regular',
        max_nodes=math.inf,
        max_time_hours=48,
        exclusive=True,
        available_cpu_cores=128,
        submit_limit=5000,
        run_limit=math.inf,
        priority=SlurmPriority.MEDIUM,
    )
    SHARED = QOSProperties(
        QoS='shared',
        max_nodes=0.5,
        max_time_hours=48,
        exclusive=False,
        submit_limit=5000,
        priority=SlurmPriority.MEDIUM,
    )


@dataclass
class SlurmProviderConfig(ProviderConfig):

    label : str = field(default="Slurm Provider", init=False)
    _parsl_provider_type : Type = field(default=SlurmProvider, init=False)
    launcher : Any = field(default=SrunLauncher, init=False)
    qos : SlurmQOS = field(default=SlurmQOS.DEBUG, init=True)
    account : str = field(default=None, init=True)
    compute_node : SystemNode = field(default=None, init=True)
    nodes_per_block : Optional[int] = field(default=1, init=True)
    max_blocks : Optional[int] = field(default=1, init=True)
    cores_per_node : Optional[int] = field(default=None, init=True)
    walltime : Optional[str | Tuple[float, int, int]] = field(default="00:00:00", init=True)
    command_timeout : Optional[float] = field(default=120.0, init=True)
    worker_init_bash_command : Optional[str] = field(default=None, init=True)

    def _to_provider_object(self) -> SlurmProvider:

        assert callable(self.launcher)
        if self.compute_node:
            if self.compute_node.type is SystemNodeType.COMPUTE_NODE:
                _constraint = 'cpu'
            else:
                raise NotImplemented
        else:
            _constraint = 'cpu'

        __qos_obj = self.qos.value
        _qos_type = __qos_obj.QoS
        _exclusive = __qos_obj.exclusive
        _account = self.account
        _nodes_per_block = self.nodes_per_block
        _cores_per_node = self.cores_per_node

        if isinstance(self.walltime, tuple):
            _walltime = format_walltime(self.walltime[0], self.walltime[1], self.walltime[2])
        else:
            _walltime = self.walltime

        _walltime = self.walltime
        _command_timeout = self.command_timeout
        _worker_init_bash_command = self.worker_init_bash_command

        #Srun Launcher Argument
        if _cores_per_node:
            _overrides = f"-c {_cores_per_node}"
            _launcher = SrunLauncher(overrides=_overrides)
        else:
            _launcher = SrunLauncher()

        input_params = {
            "launcher" : _launcher,
            "qos" : _qos_type,
            "account" : _account,
            "exclusive" : _exclusive,
            "constraint" : _constraint,
            "nodes_per_block" : _nodes_per_block,
            "cores_per_node" : _cores_per_node,
            "walltime" : _walltime,
            "command_timeout" : _command_timeout,
            "worker_init" : _worker_init_bash_command,
        }

        #Only pass non-None arguments to provider call.
        input_params = filter(lambda x, y : y is not None, input_params)
        return SlurmProvider(**input_params)


    def validate(self):

        if isinstance(self.walltime, str):
            hours, minutes, seconds = _walltime_str_to_tuple(self.walltime)
        elif isinstance(self.walltime, tuple):
            hours, minutes, seconds = self.walltime

        _qos_obj = self.qos.value
        _qos_obj.validate(
            hours=hours, minutes=minutes, seconds=seconds,
            cpu_cores=self.cores_per_node * self.nodes_per_block * self.max_blocks
        )

    def __post_init__(self):

        self.validate()


@dataclass
class SlurmHighThroughputConfig(ExecutorConfig):

    label = "Slurm High Throughput Executor"
    _executor_type = HighThroughputExecutor
    account: str = field(default=None, init=True)
    compute_node: SystemNode = field(default=None, init=True)
    nodes_per_block: Optional[int] = field(default=1, init=True)
    max_blocks: Optional[int] = field(default=1, init=True)
    cores_per_node: Optional[int] = field(default=None, init=True)
    walltime: Optional[str | Tuple[float, int, int]] = field(default="00:00:00", init=True)
    command_timeout: Optional[float] = field(default=120.0, init=True)
    worker_init_bash_command: Optional[str] = field(default=None, init=True)


    def __post_init__(self):

        self.provider = SlurmProviderConfig(
            qos=self.qos.value,
            account=self.account,
            compute_node=self.compute_node,
            nodes_per_block=self.nodes_per_block,
            max_blocks=self.max_blocks,
            cores_per_node=self.cores_per_node,
            walltime=self.walltime,
            command_timeout=self.command_timeout,
            worker_init_bash_command=self.worker_init_bash_command,
        )

    def to_executor_object(self) -> _executor_type:

        _label = self.label
        _cpu_affinity = self.cpu_affinity.value
        _max_workers_per_node = self.max_workers_per_node
        _cores_per_worker = self.cores_per_worker
        _provider_obj = self.provider.to_provider_object()

        params = {
            "label" : _label,
            "cpu_affinity" : _cpu_affinity,
            "max_workers_per_node" : _max_workers_per_node,
            "cores_per_worker" : _cores_per_worker,
            "provider" : _provider_obj,
        }

        params = filter(lambda x, y : y is not None, params)
        return self._executor_type(**params)

