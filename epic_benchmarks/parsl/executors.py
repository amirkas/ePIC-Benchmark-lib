
from epic_benchmarks.parsl import SimpleLauncherConfig
from pydantic import Field, SerializeAsAny, ValidationInfo, field_validator
from typing import ClassVar, Dict, Optional, Type, Union, Sequence, Tuple, List, Callable, Literal
from collections.abc import Mapping

from parsl.executors import *
from parsl.data_provider.staging import Staging
from parsl.executors.high_throughput.manager_selector import (
    ManagerSelector,
    RandomManagerSelector,
)
from parsl.executors.status_handling import BlockProviderExecutor
from parsl.jobs.states import JobStatus

from epic_benchmarks.parsl._base import BaseParslModel
from epic_benchmarks.container.config import ContainerConfig
from epic_benchmarks.parsl.providers import (
    ParslProviderConfig, ProviderWithWorkerInit,
    AWSProviderConfig, CondorProviderConfig, GoogleCloudProviderConfig,
    GridEngineProviderConfig, LocalProviderConfig, LSFProviderConfig,
    SlurmProviderConfig, TorqueProviderConfig, KubernetesProviderConfig,
    PBSProProviderConfig
)

ProviderUnion = Union[
    AWSProviderConfig, CondorProviderConfig, GoogleCloudProviderConfig,
    GridEngineProviderConfig, LocalProviderConfig, LSFProviderConfig,
    SlurmProviderConfig, TorqueProviderConfig, KubernetesProviderConfig,
    PBSProProviderConfig
]

class ParslExecutorConfig(BaseParslModel):

    label: str
    working_dir: Optional[str] = None

class ParslExecutorConfigWithoutContainer(ParslExecutorConfig):

    pass

class ParslExecutorConfigWithContainer(ParslExecutorConfig):

    container_config : Optional[ContainerConfig] = Field(default=None)
    provider: ProviderUnion = Field(default_factory=SimpleLauncherConfig, discriminator='config_type_name')
    launch_cmd: Optional[str] = None

    def to_parsl_config(self, exclude = None, *excludes):
        return super().to_parsl_config('container_config')

    #Update provider config worker init to initialize a container if one is provided.
    @field_validator('provider', mode='after')
    def add_container_init(cls, provider : ParslProviderConfig, info : ValidationInfo) -> ParslProviderConfig:

        container = info.data['container_config']
        if container is not None and isinstance(provider, ProviderWithWorkerInit):
            assert(isinstance(container, ContainerConfig))
            container_init = container.init_command
            new_worker_init = f"{container_init}; {provider.worker_init}"
            provider.worker_init = new_worker_init
        return provider

class ThreadPoolExecutorConfig(ParslExecutorConfigWithoutContainer):
    
    config_type_name : Literal['ThreadPoolExecutor'] = "ThreadPoolExecutor"
    config_type : ClassVar[Type] = ThreadPoolExecutor

    label : str = 'threads'
    max_threads : Optional[int] = 2
    thread_name_prefix: str = ''
    storage_access: Optional[List[Staging]] = None
    

class HighThroughputExecutorConfig(ParslExecutorConfigWithContainer):

    config_type_name : Literal['HighThroughputExecutor'] = "HighThroughputExecutor"
    config_type : ClassVar[Type] = HighThroughputExecutor

    label: str = 'HighThroughputExecutor'
    cores_per_worker: float = 1.0,
    mem_per_worker: Optional[float] = None
    max_workers_per_node: Optional[Union[int, float]] = None
    cpu_affinity : Literal['none', 'block', 'alternating', 'block-reverse'] = 'none'

    available_accelerators: SerializeAsAny[Union[int, Sequence[str]]] = []
    interchange_launch_cmd: Optional[Sequence[str]] = None
    address: Optional[str] = None
    loopback_address: str = "127.0.0.1"
    worker_ports: Optional[Tuple[int, int]] = None
    worker_port_range: Optional[Tuple[int, int]] = (54000, 55000)
    interchange_port_range: Optional[Tuple[int, int]] = (55000, 56000)
    storage_access: Optional[List[Staging]] = None
    worker_debug: bool = False
    prefetch_capacity: int = 0
    heartbeat_threshold: int = 120
    heartbeat_period: int = 30
    drain_period: Optional[int] = None,
    poll_period: int = 10
    address_probe_timeout: Optional[int] = None
    worker_logdir_root: Optional[str] = None
    manager_selector: ManagerSelector = Field(default_factory=RandomManagerSelector)
    block_error_handler: Union[bool, Callable[[BlockProviderExecutor, Dict[str, JobStatus]], None]] = True
    encrypted: bool = False

    
class MPIExecutorConfig(ParslExecutorConfigWithContainer):
    
    config_type_name : Literal['MPIExecutor'] = "MPIExecutor"
    config_type : ClassVar[Type] = MPIExecutor

    label: str = 'MPIExecutor'
    interchange_launch_cmd: Optional[str] = None
    address: Optional[str] = None
    loopback_address: str = "127.0.0.1"
    worker_ports: Optional[Tuple[int, int]] = None
    worker_port_range: Optional[Tuple[int, int]] = (54000, 55000)
    interchange_port_range: Optional[Tuple[int, int]] = (55000, 56000)
    storage_access: Optional[List[Staging]] = None
    worker_debug: bool = False
    max_workers_per_block: int = 1
    prefetch_capacity: int = 0
    heartbeat_threshold: int = 120
    heartbeat_period: int = 30
    drain_period: Optional[int] = None
    poll_period: int = 10
    address_probe_timeout: Optional[int] = None
    worker_logdir_root: Optional[str] = None
    mpi_launcher: str = "mpiexec"
    block_error_handler: Union[bool, Callable[[BlockProviderExecutor, Dict[str, JobStatus]], None]] = True
    encrypted: bool = False

class FluxExecutorConfig(ParslExecutorConfigWithContainer):

    config_type_name : Literal['FluxExecutor'] = "FluxExecutor"
    config_type : ClassVar[Type] = FluxExecutor

    label: str = "FluxExecutor"
    flux_executor_kwargs: Mapping = {}
    flux_path: Optional[str] = None
    launch_cmd: Optional[str] = None


