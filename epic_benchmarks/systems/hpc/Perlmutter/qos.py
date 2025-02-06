from typing import ClassVar
from epic_benchmarks.systems.hpc.qos import SlurmQOS, NodeList
from epic_benchmarks.systems.hpc.Perlmutter.nodes import (
    PerlmutterLoginNode, PerlmutterCpuNode, PerlmutterGpuNode,
    PerlmutterGPULessBandwidthNode, PerlmutterGpuMoreBandwidthNode
)

TOTAL_CPU_NODES = 3072
TOTAL_GPU_LOWER_BANDWIDTH_NODES = 1536
TOTAL_GPU_HIGHER_BANDWIDTH_NODES = 256
TOTAL_GPU_NODES = TOTAL_GPU_LOWER_BANDWIDTH_NODES + TOTAL_GPU_HIGHER_BANDWIDTH_NODES

class RegularQOS(SlurmQOS):
    name : ClassVar[str] = "regular"
    max_nodes : ClassVar[NodeList] = [
        PerlmutterCpuNode * TOTAL_CPU_NODES,
        PerlmutterGpuNode * TOTAL_GPU_NODES,
        PerlmutterGPULessBandwidthNode * TOTAL_GPU_LOWER_BANDWIDTH_NODES,
        PerlmutterGpuMoreBandwidthNode * TOTAL_GPU_HIGHER_BANDWIDTH_NODES,
    ]
    max_walltime : ClassVar[str] = "48:00:00"
    shared : ClassVar[bool] = False

class DebugQOS(SlurmQOS):
    name : ClassVar[str] = "debug"
    max_nodes : ClassVar[NodeList] = [
        PerlmutterCpuNode * 8,
        PerlmutterGpuNode * 8,
        PerlmutterGPULessBandwidthNode * 8,
        PerlmutterGpuMoreBandwidthNode * 8,
    ]
    max_walltime : ClassVar[str] = "00:00:30"
    shared : ClassVar[bool] = False

class SharedQOS(SlurmQOS):

    name : ClassVar[str] = "shared"
    max_nodes : ClassVar[NodeList] = [
        PerlmutterCpuNode * 0.5,
        PerlmutterGpuNode * 0.5,
        PerlmutterGPULessBandwidthNode * 0.5,
        PerlmutterGpuMoreBandwidthNode * 0.5,
    ]
    max_walltime : ClassVar[str] = "48:00:00"
    shared : ClassVar[bool] = True

class InteractiveQOS(SlurmQOS):

    name : ClassVar[str] = "interactive"
    max_nodes : ClassVar[NodeList] = [
        PerlmutterCpuNode * 4,
        PerlmutterGpuNode * 4,
        PerlmutterGPULessBandwidthNode * 4,
        PerlmutterGpuMoreBandwidthNode * 4,
    ]
    max_walltime : ClassVar[str] = "04:00:00"
    shared : ClassVar[bool] = False

class PremiumQOS(SlurmQOS):

    name : ClassVar[str] = "premium"
    max_nodes : ClassVar[NodeList] = [
        PerlmutterCpuNode * TOTAL_CPU_NODES,
        PerlmutterGpuNode * TOTAL_GPU_NODES,
        PerlmutterGPULessBandwidthNode * TOTAL_GPU_LOWER_BANDWIDTH_NODES,
        PerlmutterGpuMoreBandwidthNode * TOTAL_GPU_HIGHER_BANDWIDTH_NODES,
    ]

