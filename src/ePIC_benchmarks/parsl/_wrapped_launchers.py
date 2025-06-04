from typing import Optional, Union, Dict, Any, Type
from parsl.launchers import *
from parsl.launchers.base import Launcher
from ePIC_benchmarks.container.containers import ContainerUnion, ContainerConfigAdapter

ContainerConfigType = Union[ContainerUnion, Dict[str, Any]]

def parse_container_object(container_object : ContainerConfigType) -> ContainerUnion:

    if isinstance(container_object, dict):
        return ContainerConfigAdapter.validate_python(container_object)
    else:
        return container_object
    
class BaseWrappedLauncher:

    container_config : ContainerUnion
    containerize_launcher : bool
    parent_launcher : Launcher

    def __init__(self, container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False):

        self.container_config = parse_container_object(container_config)
        self.containerize_launcher = containerize_launcher

    def wrap_command(self, command : str) -> str:

        if self.container_config is not None and self.containerize_launcher:
            return self.container_config.init_with_extra_commands(command)
        return command

    def __call__(self, command: str, tasks_per_node: int, nodes_per_block: int) -> str:

        command = self.wrap_command(command)
        return self.parent_launcher.__call__(command, tasks_per_node, nodes_per_block)

class WrappedSimpleLauncher(BaseWrappedLauncher):

    def __init__(self, debug: bool = True, container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = SimpleLauncher(debug=debug)

class WrappedSingleNodeLauncher(BaseWrappedLauncher):

    def __init__(self, prepend: str, debug: bool = True, container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = SingleNodeLauncher(prepend=prepend, debug=debug)

class WrappedSrunLauncher(BaseWrappedLauncher):

    def __init__(self, debug: bool = True, overrides: str = '', container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = SrunLauncher(debug=debug, overrides=overrides)
    

class WrappedAprunLauncher(BaseWrappedLauncher):

    def __init__(self, debug: bool = True, overrides: str = '', container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = AprunLauncher(debug=debug, overrides=overrides)
    

class WrappedSrunMPILauncher(BaseWrappedLauncher):

    def __init__(self, debug: bool = True, overrides: str = '', container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = SrunMPILauncher(debug=debug, overrides=overrides)
    
class WrappedGnuParallelLauncher(BaseWrappedLauncher):

    def __init__(self, debug: bool = True, container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = GnuParallelLauncher(debug=debug)

class WrappedMpiExecLauncher(BaseWrappedLauncher):

    def __init__(self, debug: bool = True, bind_cmd: str = '--bind-to', overrides: str = '', container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = MpiExecLauncher(debug=debug, bind_cmd=bind_cmd, overrides=overrides)


class WrappedMpiRunLauncher(BaseWrappedLauncher):

    def __init__(self, debug: bool = True, bash_location: str = '/bin/bash', overrides: str = '', container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = MpiRunLauncher(debug=debug, bash_location=bash_location, overrides=overrides)

class WrappedJsrunLauncher(BaseWrappedLauncher):

    def __init__(self, debug: bool = True, overrides: str = '', container_config : Optional[ContainerConfigType] = None, containerize_launcher : bool = False) -> None:
        super().__init__(container_config=container_config, containerize_launcher=containerize_launcher)
        self.parent_launcher = JsrunLauncher(debug=debug, overrides=overrides)

