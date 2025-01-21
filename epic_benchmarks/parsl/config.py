from typing import Optional, Sequence, Type, Union, Literal, Callable

from parsl.config import Config
from parsl.dataflow.dependency_resolvers import DependencyResolver
from parsl.dataflow.taskrecord import TaskRecord
from parsl.monitoring import MonitoringHub
from pydantic import ConfigDict, InstanceOf, RootModel

from epic_benchmarks.parsl._base import BaseParslModel
from epic_benchmarks.parsl.executors import (
    ParslExecutorConfig, ParslExecutorConfigWithContainer,
    ThreadPoolExecutorConfig, HighThroughputExecutorConfig,
    MPIExecutorConfig, FluxExecutorConfig
)
from epic_benchmarks.container.config import ContainerConfig

ExecutorInstanceTypes = Union[
    InstanceOf[ThreadPoolExecutorConfig], InstanceOf[HighThroughputExecutorConfig],
    InstanceOf[MPIExecutorConfig], InstanceOf[FluxExecutorConfig]
]

class ExecutorList(RootModel):

    model_config = ConfigDict(strict=True)
    root : Sequence[ExecutorInstanceTypes]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]
    

class ParslConfig(BaseParslModel):

    config_type : Type = Config

    executors: Optional[ExecutorList] = None
    app_cache: bool = True
    checkpoint_files: Optional[Sequence[str]] = None
    checkpoint_mode: Union[
        None,
        Literal['task_exit'],
        Literal['periodic'],
        Literal['dfk_exit'],
        Literal['manual']
    ] = None
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
    
    def all_containers(self) -> Sequence[ContainerConfig]:

        container_lst = []
        for executor in self.executors:
            if isinstance(executor, ParslExecutorConfigWithContainer):
                executor_container = executor.container_config
                if executor_container is not None:
                    container_lst.append(executor_container)
        return container_lst
    
    # def to_parsl_config(self):

    #     return self.model_dump(exclude_unset=True, context={'option' : 'config'})


