from pydantic import Field
from typing import Literal, Type, ClassVar, Union

from epic_benchmarks.parsl._wrapped_launchers import *
from epic_benchmarks.container import *

from epic_benchmarks.parsl._base import BaseParslModel

ContainerUnion = Union[
    DockerConfig, ShifterConfig
]
class ParslLauncherConfig(BaseParslModel):

    container_config : Optional[Union[DockerConfig, ShifterConfig]] = Field(discriminator='container_type', default=None)
    containerize_launcher : bool = False
    debug : bool = Field(default=False)

class SimpleLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['SimpleLauncher'] = "SimpleLauncher"
    config_type : ClassVar[Type] = WrappedSimpleLauncher

class SingleNodeLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['SingleNodeLauncher'] = "SingleNodeLauncher"
    config_type : ClassVar[Type] = WrappedSingleNodeLauncher

    fail_on_any : bool = True

class SrunLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['SrunLauncher'] = "SrunLauncher"
    config_type : ClassVar[Type] = WrappedSrunLauncher

    overrides : str = ''
    
class AprunLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['AprunLauncher'] = "AprunLauncher"
    config_type : ClassVar[Type] = WrappedAprunLauncher

    overrides : str = ''
    

class SrunMPILauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['SrunMPILauncher'] = "SrunMPILauncher"
    config_type : ClassVar[Type] = WrappedSrunLauncher

    overrides : str
    

class GnuParallelLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal[ 'GnuParallelLauncher'] = "GnuParallelLauncher"
    config_type : ClassVar[Type] = WrappedGnuParallelLauncher


class MpiExecLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['MpiExecLauncher'] = "MpiExecLauncher"
    config_type : ClassVar[Type] = WrappedMpiExecLauncher

    bind_cmd : str = ''
    overrides : str = ''

class MpiRunLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['MpiRunLauncher'] = "MpiRunLauncher"
    config_type : ClassVar[Type] = WrappedMpiRunLauncher
    
    bash_location : str = '/bin/bash'
    overrides : str = ''

class JsrunLauncherConfig(ParslLauncherConfig):

    config_type_name : Literal['JsrunLauncher'] = "JsrunLauncher"
    config_type : ClassVar[Type] = WrappedJsrunLauncher

    overrides : str = ''
