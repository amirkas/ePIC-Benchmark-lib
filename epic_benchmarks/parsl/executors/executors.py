from abc import ABC, abstractmethod
from pydantic import Field, SerializeAsAny
from typing import ClassVar, Dict, Optional, Type, Union, Sequence, Tuple, List, Callable, Literal
from collections.abc import Mapping

from parsl.executors import *
from parsl.executors.workqueue.executor import *
from parsl.data_provider.staging import Staging
from parsl.executors.high_throughput.manager_selector import (
    ManagerSelector,
    RandomManagerSelector,
)
from parsl.executors.status_handling import BlockProviderExecutor
from parsl.jobs.states import JobStatus

from epic_benchmarks.parsl._base import BaseParslModel
from epic_benchmarks.container.containers import ContainerUnion
from epic_benchmarks.parsl.providers import (
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


class ParslExecutorConfig(BaseParslModel, ABC):

    label: str
    working_dir: Optional[str] = None

    @abstractmethod
    def get_container_config(self) -> Optional[ContainerUnion]:
        pass



class ParslExecutorConfigWithoutProvider(ParslExecutorConfig):

    def get_container_config(self):
        return None

class ParslExecutorConfigWithProvider(ParslExecutorConfig):

    # container_config : Optional[ContainerUnion] = Field(discriminator='container_type', default=None)
    provider: ProviderUnion = Field(discriminator='config_type_name')
    launch_cmd: Optional[str] = None
    
    def get_container_config(self):
        return self.provider.launcher.container_config
    
class ThreadPoolExecutorConfig(ParslExecutorConfigWithoutProvider):
    
    config_type_name : Literal['ThreadPoolExecutor'] = "ThreadPoolExecutor"
    config_type : ClassVar[Type] = ThreadPoolExecutor

    label : str = 'threads'
    max_threads : Optional[int] = 2
    thread_name_prefix: str = ''
    storage_access: Optional[List[Staging]] = None
    

class HighThroughputExecutorConfig(ParslExecutorConfigWithProvider):

    config_type_name : Literal['HighThroughputExecutor'] = "HighThroughputExecutor"
    config_type : ClassVar[Type] = HighThroughputExecutor

    label: str = 'HighThroughputExecutor'
    cores_per_worker: float = 1.0
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
    drain_period: Optional[int] = None
    poll_period: int = 10
    address_probe_timeout: Optional[int] = None
    worker_logdir_root: Optional[str] = None
    manager_selector: ManagerSelector = Field(default_factory=RandomManagerSelector)
    block_error_handler: Union[bool, Callable[[BlockProviderExecutor, Dict[str, JobStatus]], None]] = True
    encrypted: bool = False

    
class MPIExecutorConfig(ParslExecutorConfigWithProvider):
    
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

class FluxExecutorConfig(ParslExecutorConfigWithProvider):

    config_type_name : Literal['FluxExecutor'] = "FluxExecutor"
    config_type : ClassVar[Type] = FluxExecutor

    label: str = "FluxExecutor"
    flux_executor_kwargs: Mapping = Field(default_factory=dict)
    flux_path: Optional[str] = None
    launch_cmd: Optional[str] = None



class WorkQueueExecutorConfig(ParslExecutorConfigWithProvider):

    config_type_name : Literal['WorkQueueExecutor'] = "WorkQueueExecutor"
    config_type : ClassVar[Type] = WorkQueueExecutor

    label: str = "WorkQueueExecutor"
    working_dir: str = "."
    project_name: Optional[str] = None
    project_password_file: Optional[str] = None
    address: Optional[str] = None
    port: int = WORK_QUEUE_DEFAULT_PORT
    env: Optional[Dict] = None
    shared_fs: bool = False
    storage_access: Optional[List[Staging]] = None
    use_cache: bool = False
    source: bool = False
    pack: bool = False
    extra_pkgs: Optional[List[str]] = None
    autolabel: bool = False
    autolabel_window: int = 1
    autocategory: bool = True
    max_retries: int = 1
    init_command: str = ""
    worker_options: str = ""
    full_debug: bool = True
    worker_executable: str = 'work_queue_worker'
    function_dir: Optional[str] = None
    coprocess: bool = False
    scaling_cores_per_worker: int = 1


