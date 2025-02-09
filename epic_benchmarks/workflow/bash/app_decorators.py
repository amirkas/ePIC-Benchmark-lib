from parsl.app.bash import BashApp
from parsl import bash_app
from parsl.dataflow.dflow import DataFlowKernel
from typing import Callable, Optional, Literal, Union, Sequence, List

from epic_benchmarks.container._base import BaseContainerConfig
from epic_benchmarks.container.containers import ContainerUnion

def containerized_bash_app(function: Optional[Callable] = None,
                            data_flow_kernel: Optional[DataFlowKernel] = None,
                            cache: bool = False,
                            container : Optional[ContainerUnion] = None,
                            executors: Union[List[str], Literal['all']] = 'all',
                            ignore_for_cache: Optional[Sequence[str]] = None):

    def app_container_decorator(func : Callable) -> Callable:

        def wrapper(*args, **kwargs) -> str:

            result = func(*args, **kwargs)
            assert(isinstance(result, str))
            if container is not None:
                return container.init_with_extra_commands(result)
            else:
                return result
        return wrapper
            
    def bash_app_decorator(func : Callable) -> Callable:

        def wrapper(f: Callable) -> BashApp:
            return BashApp(f,
                           data_flow_kernel=data_flow_kernel,
                           cache=cache,
                           executors=executors,
                           ignore_for_cache=ignore_for_cache)
        return wrapper(func)
    if function is not None:
        containerized_func = app_container_decorator(function)
        return bash_app_decorator(containerized_func)
    return bash_app_decorator
    
    