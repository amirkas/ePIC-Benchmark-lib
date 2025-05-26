from ePIC_benchmarks.parsl.config import ParslConfig
from ePIC_benchmarks.parsl.executors import HighThroughputExecutorConfig
from ePIC_benchmarks.parsl.providers import LocalProviderConfig
from ePIC_benchmarks.parsl.launchers import SrunLauncherConfig

EXAMPLE_PARSL_CONFIG = ParslConfig(
    executors=[
        HighThroughputExecutorConfig(
            label="HTEC_Executor",
            cores_per_worker=2,
            max_workers_per_node=10,
            provider=LocalProviderConfig(
                nodes_per_block = 1,
                launcher=SrunLauncherConfig(overrides='-c 20'),
                max_blocks=1,
                init_blocks=1,
            ),
        ),
    ],
)