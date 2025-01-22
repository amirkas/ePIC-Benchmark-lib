from pydantic import Field
from typing import Literal, Type, TypeVar, ClassVar

from parsl.launchers.base import Launcher
from parsl.launchers import *

from epic_benchmarks.parsl._base import BaseParslModel
from epic_benchmarks.container.config import ContainerConfig

class ParslLauncherConfig(BaseParslModel):

    debug : bool = Field(default=False)

    def containerize(self, container : ContainerConfig) -> None:

        pass

class SimpleLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['SimpleLauncher'] = "SimpleLauncher"
    config_type : ClassVar[Type] = SimpleLauncher

    def containerize(self, container) -> None:
        pass

class SingleNodeLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['SingleNodeLauncher'] = "SingleNodeLauncher"
    config_type : ClassVar[Type] = SingleNodeLauncher

    fail_on_any : bool = True
    def containerize(self, container):
        #TODO: Implement
        # self.prepend = container.containerize_command()
        pass

class SrunLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['SrunLauncher'] = "SrunLauncher"
    config_type : ClassVar[Type] = SrunLauncher

    overrides : str = ''
    def containerize(self, container):
        pass
    

class AprunLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['AprunLauncher'] = "AprunLauncher"
    config_type : ClassVar[Type] = AprunLauncher

    overrides : str = ''
    def containerize(self, container):
        pass
    

class SrunMPILauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['SrunMPILauncher'] = "SrunMPILauncher"
    config_type : ClassVar[Type] = SrunMPILauncher

    overrides : str
    def containerize(self, container):
        pass
    

class GnuParallelLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal[ 'GnuParallelLauncher'] = "GnuParallelLauncher"
    config_type : ClassVar[Type] = GnuParallelLauncher

    def containerize(self, container):
        pass

class MpiExecLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['MpiExecLauncher'] = "MpiExecLauncher"
    config_type : ClassVar[Type] = MpiExecLauncher

    bind_cmd : str = ''
    overrides : str = ''
    def containerize(self, container):
        pass

class MpiRunLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['MpiRunLauncher'] = "MpiRunLauncher"
    config_type : ClassVar[Type] = MpiRunLauncher
    
    bash_location : str = '/bin/bash'
    overrides : str = ''
    def containerize(self, container):
        pass

class JsrunLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['JsrunLauncher'] = "JsrunLauncher"
    config_type : ClassVar[Type] = JsrunLauncher

    overrides : str = ''
    def containerize(self, container):
        pass

class WrappedLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['WrappedLauncher'] = "WrappedLauncher"
    config_type : ClassVar[Type] = WrappedLauncher

    prepend : str = ''
    def containerize(self, container):
        #TODO: Fix
        # self.prepend = container.containerize_command()
        pass