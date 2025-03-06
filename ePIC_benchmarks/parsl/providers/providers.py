from pydantic import Field
from typing import ClassVar, List, Literal, Optional, Tuple, Type, Dict, Union

from parsl.providers import *

from ePIC_benchmarks.parsl._base import BaseParslModel
from ePIC_benchmarks.parsl.launchers import (
    SimpleLauncherConfig, SingleNodeLauncherConfig,
    SrunLauncherConfig, AprunLauncherConfig, SrunMPILauncherConfig,
    GnuParallelLauncherConfig, MpiExecLauncherConfig, MpiRunLauncherConfig,
    JsrunLauncherConfig 
)

LauncherUnion= Union[
    SimpleLauncherConfig, SingleNodeLauncherConfig, SrunLauncherConfig,
    AprunLauncherConfig, SrunMPILauncherConfig, GnuParallelLauncherConfig,
    MpiExecLauncherConfig, MpiRunLauncherConfig, JsrunLauncherConfig, 
]

class ParslProviderConfig(BaseParslModel):

    launcher : Optional[LauncherUnion] = Field(default=None, discriminator='config_type_name')

class ProviderWithWorkerInit(ParslProviderConfig):

    worker_init : str = ''

class ProviderWithoutWorkerInit(ParslProviderConfig):

    pass

class AWSProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['AWSProvider'] = "AWSProvider"
    config_type : ClassVar[Type] = AWSProvider

    image_id : str
    key_name : str
    init_blocks : int = 1
    min_blocks : int = 0
    max_blocks : int = 10
    nodes_per_block : int = 1
    parallelism : int = 1

    instance_type : str ='t2.small'
    region : str ='us-east-2'
    spot_max_bid : float = 0

    key_file : Optional[str] = None
    profile : Optional[str] = None
    iam_instance_profile_arn : str =''

    state_file : Optional[str] = None
    walltime : str ="01:00:00"
    linger : bool =False

class CondorProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['CondorProvider'] = "CondorProvider"
    config_type : ClassVar[Type] = CondorProvider

    nodes_per_block: int = 1
    cores_per_slot: Optional[int] = None
    mem_per_slot: Optional[float] = None
    init_blocks: int = 1
    min_blocks: int = 0
    max_blocks: int = 1
    parallelism: float = 1
    environment: Optional[Dict[str, str]] = None
    project: str = ''
    scheduler_options: str = ''
    transfer_input_files: List[str] = []
    walltime: str = "00:10:00"
    requirements: str = ''
    cmd_timeout: int = 60
    cmd_chunk_size: int = 100
    

class GoogleCloudProviderConfig(ProviderWithoutWorkerInit):

    config_type_name : Literal['GoogleCloudProvider'] = "GoogleCloudProvider"
    config_type : ClassVar[Type] = GoogleCloudProvider

    project_id : str
    key_file : str
    region : str
    os_project : str
    os_family : str
    google_version : str = 'v1',
    instance_type : str ='n1-standard-1',
    init_blocks : int = 1,
    min_blocks : int = 0,
    max_blocks : int = 10,
    parallelism : float = 1
    

class GridEngineProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['GridEngineProvider'] = "GridEngineProvider"
    config_type : ClassVar[Type] = GridEngineProvider

    nodes_per_block : int = 1
    init_blocks : int = 1
    min_blocks : int = 0
    max_blocks : int = 1
    parallelism : float = 1
    walltime : str ="00:10:00"
    scheduler_options : str =''
    cmd_timeout: int = 60
    queue : Optional[str] = None

class LocalProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['LocalProvider'] = "LocalProvider"
    config_type : ClassVar[Type] = LocalProvider

    nodes_per_block : int = 1
    init_blocks : int = 1
    min_blocks : int = 0
    max_blocks : int = 1
    cmd_timeout : int = 30
    parallelism : float = 1

class LSFProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['LSFProvider'] = "LSFProvider"
    config_type : ClassVar[Type] = LSFProvider

    nodes_per_block : int = 1
    cores_per_block : Optional[int] = None
    cores_per_node : Optional[int] = None
    init_blocks : int = 1
    min_blocks : int = 0
    max_blocks : int = 1
    parallelism : float = 1
    walltime : str ="00:10:00"
    scheduler_options : str =''
    project : Optional[str] = None
    queue : Optional[str] = None
    cmd_timeout : int = 120
    bsub_redirection : bool =False
    request_by_nodes : bool =True

class SlurmProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['SlurmProvider'] = "SlurmProvider"
    config_type : ClassVar[Type] = SlurmProvider

    partition: Optional[str] = None
    account: Optional[str] = None
    qos: Optional[str] = None
    constraint: Optional[str] = None
    clusters: Optional[str] = None
    nodes_per_block: int = 1
    cores_per_node: Optional[int] = None
    mem_per_node: Optional[int] = None
    init_blocks: int = 1
    min_blocks: int = 0
    max_blocks: int = 1
    parallelism: float = 1
    walltime: str = "00:10:00"
    scheduler_options: str = ''
    regex_job_id: str = r"Submitted batch job (?P<id>\S*)"
    cmd_timeout: int = 10
    exclusive: bool = True

class TorqueProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['TorqueProvider'] = "TorqueProvider"
    config_type : ClassVar[Type] = TorqueProvider

    account : Optional[str] = None
    queue : Optional[str] = None
    scheduler_options : str = ''
    nodes_per_block : int = 1
    init_blocks : int = 1
    min_blocks : int = 0
    max_blocks : int = 1
    parallelism : float = 1
    walltime : str = "00:20:00"
    cmd_timeout : int = 120

class KubernetesProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['KubernetesProvider'] = "KubernetesProvider"
    config_type : ClassVar[Type] = KubernetesProvider

    image: str
    namespace: str = 'default'
    nodes_per_block: int = 1
    init_blocks: int = 4
    min_blocks: int = 0
    max_blocks: int = 10
    max_cpu: float = 2
    max_mem: str = "500Mi"
    init_cpu: float = 1
    init_mem: str = "250Mi"
    parallelism: float = 1
    pod_name: Optional[str] = None
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    run_as_non_root: bool = False
    secret: Optional[str] = None
    persistent_volumes: List[Tuple[str, str]] = Field(default_factory=list)
    service_account_name: Optional[str] = None
    annotations: Optional[Dict[str, str]] = None

class PBSProProviderConfig(ProviderWithWorkerInit):

    config_type_name : Literal['PBSProProvider'] = "PBSProProvider"
    config_type : ClassVar[Type] = PBSProProvider

    account : Optional[str] = None
    queue : Optional[str] = None
    scheduler_options : str = ''
    select_options : str =''
    nodes_per_block : int = 1
    cpus_per_node : int = 1
    init_blocks : int = 1
    min_blocks : int = 0
    max_blocks : int = 1
    parallelism : float = 1
    walltime : str = "00:20:00"
    cmd_timeout : int = 120
