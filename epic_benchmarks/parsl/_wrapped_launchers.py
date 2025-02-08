from typing import Optional, Union, Dict, Any
from parsl.launchers import *
from epic_benchmarks.container.containers import ContainerUnion, ContainerConfigAdapter

ContainerConfigType = Union[ContainerUnion, Dict[str, Any]]


def parse_container_object(container_object : ContainerConfigType) -> ContainerUnion:

    if isinstance(container_object, dict):
        return ContainerConfigAdapter.validate_python(container_object)
    else:
        return container_object
    
class BaseWrappedLauncher:

    
    container_config : ContainerUnion
    containerize_launcher : bool

    def __init__(self, container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False, **kwargs):

        super().__init__(**kwargs)
        self.container_config = parse_container_object(container_config)
        self.containerize_launcher = containerize_launcher

    def wrap_command(self, command : str) -> str:

        if self.container_config is not None and self.containerize_launcher:
            return self.container_config.init_with_extra_commands(command)
        return command

    def __call__(self, command: str, tasks_per_node: int, nodes_per_block: int) -> str:

        command = self.wrap_command(command)
        return super().__call__(command, tasks_per_node, nodes_per_block)


class WrappedSimpleLauncher(BaseWrappedLauncher, SimpleLauncher):

    pass

class WrappedSingleNodeLauncher(BaseWrappedLauncher, SingleNodeLauncher):

    pass

class WrappedSrunLauncher(BaseWrappedLauncher, SrunLauncher):

    def __init__(
            self,
            container_config : Optional[ContainerConfigType] = None,
            containerize_launcher : bool = False,
            debug: bool = True, overrides: str = ''):
        
        super().__init__(
            container_config=container_config,
            containerize_launcher=containerize_launcher,
            debug=debug,
            overrides=overrides
        )
        

class WrappedAprunLauncher(BaseWrappedLauncher, AprunLauncher):

    pass

class WrappedSrunMPILauncher(BaseWrappedLauncher, SrunMPILauncher):

    pass

class WrappedGnuParallelLauncher(BaseWrappedLauncher, GnuParallelLauncher):

    pass

class WrappedMpiExecLauncher(BaseWrappedLauncher, MpiExecLauncher):

    pass

class WrappedMpiRunLauncher(BaseWrappedLauncher, MpiRunLauncher):

    pass

class WrappedJsrunLauncher(BaseWrappedLauncher, JsrunLauncher):

    pass

