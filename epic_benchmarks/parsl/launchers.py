from pydantic import Field
from typing import Type, TypeVar

from parsl.launchers.base import Launcher
from parsl.launchers import *

from epic_benchmarks.parsl._base import BaseParslModel
from epic_benchmarks.container.config import ContainerConfig

ParslLauncherType = TypeVar('Launcher', bound=Launcher)

class ParslLauncherConfig(BaseParslModel):

    debug : bool = Field(default=False)

    def containerize(self, container : ContainerConfig) -> None:

        pass

class SimpleLauncherConfig(ParslLauncherConfig):

    config_type : Type = SimpleLauncher

    def containerize(self, container) -> None:
        pass

class SingleNodeLauncherConfig(ParslLauncherConfig):

    config_type : Type = SingleNodeLauncher

    prepend : str = ''
    def containerize(self, container):
        #TODO: Implement
        # self.prepend = container.containerize_command()
        pass

class SrunLauncherConfig(ParslLauncherConfig):

    config_type : Type = SrunLauncher

    fail_on_any : bool = False
    def containerize(self, container):
        pass
    

class AprunLauncherConfig(ParslLauncherConfig):

    config_type : Type = AprunLauncher

    overrides : str = ''
    def containerize(self, container):
        pass
    

class SrunMPILauncherConfig(ParslLauncherConfig):

    config_type : Type = SrunMPILauncher

    overrides : str
    def containerize(self, container):
        pass
    

class GnuParallelLauncherConfig(ParslLauncherConfig):

    config_type : Type = GnuParallelLauncher

    def containerize(self, container):
        pass

class MpiExecLauncherConfig(ParslLauncherConfig):

    config_type : Type = MpiExecLauncher

    bind_cmd : str = ''
    overrides : str = ''
    def containerize(self, container):
        pass

class MpiRunLauncherConfig(ParslLauncherConfig):

    config_type : Type = MpiRunLauncher
    
    bash_location : str = '/bin/bash'
    overrides : str = ''
    def containerize(self, container):
        pass

class JsrunLauncherConfig(ParslLauncherConfig):

    config_type : Type = JsrunLauncher

    overrides : str = ''
    def containerize(self, container):
        pass

class WrappedLauncherConfig(ParslLauncherConfig):

    config_type : Type = WrappedLauncher

    prepend : str = ''
    def containerize(self, container):
        #TODO: Fix
        # self.prepend = container.containerize_command()
        pass