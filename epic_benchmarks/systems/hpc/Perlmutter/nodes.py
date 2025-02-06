from typing import ClassVar
from epic_benchmarks.systems.hpc.node import BaseSystemNode

class PerlmutterNode(BaseSystemNode):
    pass

PerlmutterLoginNode = PerlmutterNode(
    available_cpu_cores=128,
    available_ram=512,
    cpu_multiplicative=True
)

PerlmutterCpuNode = PerlmutterNode(
    available_cpu_cores=128,
    available_ram=512,
    cpu_multiplicative=True
)

PerlmutterGpuNode = PerlmutterNode(
    available_cpu_cores=64,
    available_gpu_cores=4,
    available_ram=256,
    cpu_multiplicative=True,
    gpu_multiplicative=True
)

PerlmutterGpuMoreBandwidthNode = PerlmutterNode(
    available_cpu_cores=64,
    available_gpu_cores=4,
    available_ram=256,
    cpu_multiplicative=True,
    gpu_multiplicative=True
)

PerlmutterGPULessBandwidthNode = PerlmutterNode(
    available_cpu_cores=64,
    available_gpu_cores=4,
    available_ram=256,
    cpu_multiplicative=True,
    gpu_multiplicative=True
)


