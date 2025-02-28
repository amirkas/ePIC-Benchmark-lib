import os
from typing import Annotated, Optional, Sequence, Type, Union, Literal, Callable, ClassVar

from parsl.config import Config
from parsl.dataflow.dependency_resolvers import DependencyResolver
from parsl.dataflow.taskrecord import TaskRecord
from parsl.monitoring import MonitoringHub
from pydantic import ConfigDict, Field, RootModel, SerializeAsAny, field_validator, ValidationInfo

from ePIC_benchmarks.parsl._base import BaseParslModel
from ePIC_benchmarks.parsl.executors import (
    ThreadPoolExecutorConfig, HighThroughputExecutorConfig,
    MPIExecutorConfig, FluxExecutorConfig, WorkQueueExecutorConfig
)
from ePIC_benchmarks.parsl.executors.executors import ParslExecutorConfigWithProvider, ParslExecutorConfig
from ePIC_benchmarks.container.containers import ContainerUnion
from ePIC_benchmarks.parsl.launchers.launchers import ParslLauncherConfig
from ePIC_benchmarks.container._base import BaseContainerConfig

ExecutorUnion = Union[
    ThreadPoolExecutorConfig, HighThroughputExecutorConfig,
    MPIExecutorConfig, FluxExecutorConfig, WorkQueueExecutorConfig
]

Discriminated_Executor = Annotated[ExecutorUnion, Field(discriminator='config_type_name')]

def std_autopath(run_dir : str, task_record : TaskRecord, kw):

    label = task_record['kwargs'].get('label')
    task_id = task_record['id']
    return os.path.join(
        run_dir,
        'task_logs',
        str(int(task_id / 10000)).zfill(4),
        'task_{}_{}.{}'.format(
            str(task_id).zfill(4), 
            label,
            kw    
        )
    )

class ExecutorList(RootModel):

    model_config = ConfigDict(strict=True)
    root : SerializeAsAny[Sequence[Discriminated_Executor]]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]
    

class ParslConfig(BaseParslModel):

    model_config = ConfigDict(validate_assignment=True)

    config_type_name : Literal['Config'] = "Config" 
    config_type : ClassVar[Type] = Config

    executors: Optional[ExecutorList] = Field(default=None)
    app_cache: bool = True
    checkpoint_files: Optional[Sequence[str]] = None
    checkpoint_mode: Union[
        None,
        Literal['task_exit'],
        Literal['periodic'],
        Literal['dfk_exit'],
        Literal['manual']
    ] = 'task_exit'
    checkpoint_period: Optional[str] = None
    dependency_resolver: Optional[DependencyResolver] = None
    exit_mode: Literal['cleanup', 'skip', 'wait'] = 'cleanup'
    garbage_collect: bool = True
    internal_tasks_max_threads: int = 10
    retries: int = 0
    retry_handler: Optional[Callable[[Exception, TaskRecord], float]] = None
    run_dir: str = 'runinfo'
    std_autopath: Optional[Callable] = None
    strategy: Optional[str] = 'simple'
    strategy_period: Union[float, int] = 5
    max_idletime: float = 120.0
    monitoring: Optional[MonitoringHub] = None
    usage_tracking: int = 0
    project_name: Optional[str] = None
    initialize_logging: bool = True

    @field_validator('std_autopath', mode='after')
    def set_log_autopath(cls, autopath, info : ValidationInfo) -> Callable:

        rundir = info.data['run_dir']
        return lambda x, y : std_autopath(rundir, x, y)


    def all_executor_labels(self):

        executor_labels = []
        for executor in self.executors:
            executor_labels.append(executor.label)
        return executor_labels

    def executor_by_label(self, label : str) -> ParslExecutorConfig:

        for executor in self.executors:
            if executor.label == label:
                return executor
        err = f"Could not find executor with label '{label}'."
        raise ValueError(err)
    
    def all_containers(self) -> Sequence[BaseContainerConfig]:

        container_lst = []
        for executor in self.executors:
            if isinstance(executor, ParslExecutorConfigWithProvider):
                provider = executor.provider
                launcher = provider.launcher
                assert(isinstance(launcher, ParslLauncherConfig))
                if launcher.container_config is not None:
                    container_lst.append(launcher.container_config)

        return container_lst
    
    def executor_container(self, executor_label : str) -> Optional[ContainerUnion]:

        executor = self.executor_by_label(executor_label)
        return executor.get_container_config()
    
    
    


