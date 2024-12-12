from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Tuple, List, Type
from parsl.providers import SlurmProvider


class SystemNodeType(Enum):

    LOGIN = "login"
    CPU = "cpu"
    GPU = "gpu"

@dataclass(frozen=True, kw_only=True)
class SystemNode:
    type : SystemNodeType
    num_cpus : int
    cores_per_cpu : int
    num_gpus : int
    ram : int
    storage : Optional[int] = field(default=None)
    threads_per_core: Optional[int] = field(default=2)
    vram : Optional[int] = field(default=None)
    cpu_model : Optional[str] = field(default=None, repr=True)
    gpu_model : Optional[str] = field(default=None, repr=True)

    def validate_cpu_request(self, cpu_core_req : int):

        total_cpu_cores = self.num_cpus * self.cores_per_cpu
        if cpu_core_req > total_cpu_cores:
            err = (f"Requested CPU cores exceeds available CPU cores"
                   f"for '{self.type.value}'. "
                   f"\n Available cores: {total_cpu_cores}"
            )
            raise ValueError(err)



@dataclass(frozen=True, kw_only=True)
class ClusterManager:
     name : str
     parsl_config : Type


@dataclass(frozen=True, kw_only=True)
class SystemArchitecture:

    system_name : str = field(default="System Name", repr=True)
    node_map : Dict[str, Tuple[SystemNodeType, int]] = field(default_factory=dict, repr=True)
    cluster_providers : List[ClusterManager] = field(default_factory=list, repr=True)


#Supported Cluster Managers:

@dataclass(frozen=True, kw_only=True)
class Slurm:

    name = "Slurm"
    parsl_config = SlurmProvider



#Perlmutter Architecture Definition

PERLMUTTER_LOGIN_NODE = SystemNode(
    type=SystemNodeType.LOGIN,
    num_cpus=2,
    cores_per_cpu=64,
    num_gpus=1,
    ram=512,
    storage=960,
    cpu_model="AMD EPYC 7713",
    gpu_model="NVIDIA A100"
)

PERLMUTTER_CPU_NODE = SystemNode(
    type=SystemNodeType.CPU,
    num_cpus=2,
    cores_per_cpu=64,
    num_gpus=0,
    ram=512,
    cpu_model="AMD EPYC 7763"
)

PERLMUTTER_GPU_40GB_NODE = SystemNode(
    type=SystemNodeType.GPU,
    num_cpus=1,
    cores_per_cpu=64,
    num_gpus=4,
    ram=256,
    vram=40,
    cpu_model="AMD EPYC 7763",
    gpu_model="NVIDIA A100 (Ampere)"
)

PERLMUTTER_GPU_80GB_NODE = SystemNode(
    type=SystemNodeType.GPU,
    num_cpus=1,
    cores_per_cpu=64,
    num_gpus=4,
    ram=256,
    vram=80,
    cpu_model="AMD EPYC 7763",
    gpu_model="NVIDIA A100 (Ampere)"
)


@dataclass(frozen=True)
class Perlmutter(SystemArchitecture):

    system_name = "Perlmutter"
    node_map = {
        "login" : (PERLMUTTER_LOGIN_NODE, 40),
        "cpu" : (PERLMUTTER_CPU_NODE, 3072),
        "gpu 40GB" : (PERLMUTTER_GPU_40GB_NODE, 1536),
        "gpu 80GB" : (PERLMUTTER_GPU_80GB_NODE, 256),
    }
    cluster_providers = [Slurm]



