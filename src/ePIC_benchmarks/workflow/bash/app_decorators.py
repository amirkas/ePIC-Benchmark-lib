# from parsl.app.bash import BashApp
# from parsl.dataflow.dflow import DataFlowKernel
# from typing import Callable, Optional, Literal, Union, Sequence, List
# from parsl import AUTO_LOGNAME

from parsl import bash_app

# from ePIC_benchmarks.container._base import BaseContainerConfig
# from ePIC_benchmarks.container.containers import ContainerUnion

#Decorates the bash app so that it can be run inside a container
# def bash_app(function: Optional[Callable] = None,
#                             data_flow_kernel: Optional[DataFlowKernel] = None,
#                             cache: bool = False,
#                             container : Optional[ContainerUnion] = None,
#                             executors: Union[List[str], Literal['all']] = 'all',
#                             ignore_for_cache: Optional[Sequence[str]] = None):

#     def app_container_decorator(func : Callable) -> Callable:

#         def wrapper(*args, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME, label=func.__name__, **kwargs) -> str:

#             result = func(*args, stdout=stdout, stderr=stderr, label=label, **kwargs)
#             assert(isinstance(result, str))
#             if container is not None:
#                 return container.init_with_extra_commands(result)
#             else:
#                 return result
#         return wrapper
            
#     def bash_app_decorator(func : Callable) -> Callable:

#         def wrapper(f: Callable) -> BashApp:
#             return BashApp(f,
#                            data_flow_kernel=data_flow_kernel,
#                            cache=cache,
#                            executors=executors,
#                            ignore_for_cache=ignore_for_cache)
#         return wrapper(func)
#     if function is not None:
#         containerized_func = app_container_decorator(function)
#         return bash_app_decorator(containerized_func)
#     return bash_app_decorator
    
    