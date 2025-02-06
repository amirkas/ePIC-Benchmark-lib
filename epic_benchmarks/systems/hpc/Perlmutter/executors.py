from typing import Callable, Dict, List, Optional, Self, Sequence, Tuple, Union
from pydantic import Field, SerializeAsAny, model_validator, field_validator
from parsl.executors.high_throughput.manager_selector import (
    ManagerSelector,
    RandomManagerSelector,
)
from parsl.data_provider.staging import Staging
from parsl.executors.status_handling import BlockProviderExecutor
from parsl.jobs.states import JobStatus
from epic_benchmarks.parsl.executors import HighThroughputExecutorConfig, ThreadPoolExecutor
from epic_benchmarks.parsl.providers import SlurmProviderConfig, LocalProviderConfig
from epic_benchmarks.systems.hpc.Perlmutter.nodes import (
    PerlmutterLoginNode, PerlmutterCpuNode,
    PerlmutterGPULessBandwidthNode, PerlmutterGpuMoreBandwidthNode
)

class HighThroughputExecutor(HighThroughputExecutorConfig):

    available_accelerators: SerializeAsAny[Union[int, Sequence[str]]] = Field(init=False, default_factory=list)
    interchange_launch_cmd: Optional[Sequence[str]] = Field(init=False, default=None)
    address: Optional[str] = Field(init=False, default=None)
    loopback_address: str = Field(init=False, default="127.0.0.1")
    worker_ports: Optional[Tuple[int, int]] = Field(init=False, default=None)
    worker_port_range: Optional[Tuple[int, int]] = Field(init=False, default=(54000, 55000))
    interchange_port_range: Optional[Tuple[int, int]] = Field(init=False, default=(55000, 56000))
    storage_access: Optional[List[Staging]] = Field(init=False, default=None)
    worker_debug: bool = Field(init=False, default=False)
    prefetch_capacity: int = Field(init=False, default=0)
    heartbeat_threshold: int = Field(init=False, default=120)
    heartbeat_period: int = Field(init=False, default=30)
    drain_period: Optional[int] = Field(init=False, default=None)
    poll_period: int = Field(init=False, default=10)
    address_probe_timeout: Optional[int] = Field(init=False, default=None)
    worker_logdir_root: Optional[str] = Field(init=False, default=None)
    manager_selector: ManagerSelector = Field(default_factory=RandomManagerSelector)
    block_error_handler: Union[bool, Callable[[BlockProviderExecutor, Dict[str, JobStatus]], None]] = Field(init=False, default=True)
    encrypted: bool = Field(init=False, default=False)

    @model_validator(mode='after')
    def validate_resources(self) -> Self:

        if self.max_workers_per_node is not None:
            max_cores = self.cores_per_worker * self.max_workers_per_node
        else:
            max_cores = self.cores_per_worker
        if max_cores > 128:
            err = "Max cores per node cannot exceed 128."
            err += "Got cores per worker x max_workers_per node ≡ "
            err += f"{self.cores_per_worker} x {self.max_workers_per_node} = {max_cores}"
            raise ValueError(err)
        
        if not isinstance(self.provider, (SlurmProviderConfig, LocalProviderConfig)):
            err = f"Must use a SlurmProvider or LocalProvider. Got {self.provider.config_type.__name__}"
            raise ValueError(err)

        #TODO: Check Perlmutter Node memory constraints
        
        return self

        