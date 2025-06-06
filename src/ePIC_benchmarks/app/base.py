# import abc
# from dataclasses import dataclass, Field
# from typing import Optional, Union, ClassVar, Literal, Sequence
# from ePIC_benchmarks.workflow import WorkflowConfig


# @dataclass
# class EpicApp(abc.ABC):

#     app_type : ClassVar[Literal['python', 'bash', 'join']]
#     workflow_config : WorkflowConfig

#     executors : Optional[Union[str, Sequence[str]]] = None
#     cache : bool = False
#     ignore_for_cache : bool = False

#     def __post_init__(self):

#         if self.executors is None:
#             return

#         workflow_executor_names = self.workflow_config.parsl_executor_names()
#         if isinstance(self.executors, str) and self.executors not in workflow_executor_names:
#             err = (
#                 f"Executor {self.executors} is not an Executor listed in the WorkflowConfig.\n"
#                 f"Valid executors to use are {", ".join(workflow_executor_names)}."
#             )
#             raise ValueError(err)
#         else:
            
#             for exec_name in self.executors:
#                 if exec_name not in workflow_executor_names:
#                     err = (
#                         f"Executor {exec_name} is not an Executor listed in the WorkflowConfig.\n"
#                         f"Valid executors to use are {", ".join(workflow_executor_names)}."
#                     )
#                     raise ValueError(err)

#     @abc.abstractmethod
#     def __call__(self, *args, **kwds):
#         pass

# @dataclass
# class EpicBashApp(EpicApp):

#     app_type = 'bash'
    




