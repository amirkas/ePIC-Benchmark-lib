from ePIC_benchmarks.workflow import WorkflowConfig
from ePIC_benchmarks.parsl.config import ParslConfig
from ePIC_benchmarks.parsl.executors import HighThroughputExecutorConfig
from ePIC_benchmarks.parsl.providers import SlurmProviderConfig
from ePIC_benchmarks.parsl.launchers import SrunLauncherConfig
from typing import Literal, Union
from ...example_benchmark import EXAMPLE_BENCHMARK_CONFIG

#Assign the values for:
# - the number of requested nodes and the cpu cores
# - the maximum number of physical cores each task can use.  
NUM_NODES : int = ...
CORES_PER_WORKER : Union[int, float] = ...
QUALITY_OF_SERVICE : Literal["regular", "debug", "shared"] = ...
ACCOUNT : str = ...
#Walltime must be formatted with the pattern: 'hh:mm:ss'
WALLTIME : str = ...

#The maximum number of available cores for a Perlmutter CPU node is 128. 
#When using the shared QOS, this may be lower which means you should change this value.
MAX_AVAIALBLE_CORES_PER_NODE = 128

#Parsl CPU Node has 128 physical cores
assert CORES_PER_WORKER <= MAX_AVAIALBLE_CORES_PER_NODE

#Do not change this value
MAX_WORKERS_PER_NODE = MAX_AVAIALBLE_CORES_PER_NODE // CORES_PER_WORKER

PERLMUTTER_LOCAL_PARSL_CONFIG = ParslConfig(
    executors=[
        HighThroughputExecutorConfig(
            label="HTEC_Executor", #Optionally update this to a name of your choice.
            cores_per_worker=CORES_PER_WORKER,
            max_workers_per_node=MAX_WORKERS_PER_NODE,
            provider=SlurmProviderConfig(
                nodes_per_block=NUM_NODES,
                init_blocks=1,
                max_blocks=1,
                account=ACCOUNT,
                qos=QUALITY_OF_SERVICE,
                walltime=WALLTIME,
                #Srun expects the number of hyperthreads to use, which is double the number of physical cores. 
                launcher=SrunLauncherConfig(overrides=f'-c {MAX_AVAIALBLE_CORES_PER_NODE * 2}')
            )
        )
    ]
)

PERLMUTER_LOCAL_WORKFLOW_CONFIG = WorkflowConfig(
    name="Workflow", #Optionally update this to a name of your choice.
    benchmarks=[EXAMPLE_BENCHMARK_CONFIG], #Update this to a list of your own BenchmarkConfigs
    parsl_config=PERLMUTTER_LOCAL_PARSL_CONFIG,
    #Add additional workflow parameters here
)

#Save the workflow config to a YML file for future reference.
PERLMUTER_LOCAL_WORKFLOW_CONFIG.save_to_file("workflow_config.yml")