from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.providers import SlurmProvider
from parsl.providers import LocalProvider
from parsl.channels import LocalChannel
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_interface
from parsl import DataFlowKernel
from epic_benchmarks.configurations.benchmark_suite_config import BenchmarkSuiteConfig

def format_walltime(hours, minutes, seconds):
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def HeadlessConfig(num_cores_per_node : int, num_cores_per_worker : int, num_nodes : int, rundir="runinfo"):
    if num_cores_per_node > 128:
        raise Exception("A node has maximum of 128 cores")
    if num_cores_per_node < 1:
        raise Exception("Must use at least 1 core")

    headless_config = Config(
            executors=[
                HighThroughputExecutor(
                    label="HTEX_Headless",
                    max_workers_per_node=num_cores_per_node // num_cores_per_worker,
                    cores_per_worker=num_cores_per_worker,
                    provider=LocalProvider(
                        channel=LocalChannel(),
                        launcher=SrunLauncher(overrides="-c {cores}".format(cores=num_cores_per_node)),
                        nodes_per_block=num_nodes,
                        cmd_timeout=120,
                    ),
                ),
            ],
            strategy=None,
            run_dir=rundir
        )
    return headless_config

def SlurmProviderConfig(num_nodes : int, num_cores_per_node : int, charge_account : str, walltime_hours : int, walltime_mins : int, walltime_secs=0, QoS="debug", num_cores_per_worker=1, rundir="runinfo"):
    exclusive_bool = True
    if QoS == 'shared':
        exclusive_bool = False
    slurm_config = Config(
        executors=[
            HighThroughputExecutor(
                label="htex_SlurmProvider",
                cpu_affinity='block',
                max_workers_per_node=num_cores_per_node // num_cores_per_worker,
                cores_per_worker=num_cores_per_worker,
                provider=SlurmProvider(
                    launcher=SrunLauncher(overrides="-c {cores}".format(cores=num_cores_per_node)),
                    qos=QoS,
                    account = charge_account,
                    constraint='cpu',
                    exclusive=exclusive_bool,
                    nodes_per_block=num_nodes,
                    cores_per_node=num_cores_per_node,
                    walltime=format_walltime(walltime_hours, walltime_mins, walltime_secs),
                    cmd_timeout=120,
                    worker_init='''
shifterimg pull eicweb/jug_xl:24.10.1-stable
module load python
source activate epic_benchmarks
'''
                ),
            ),
        ],
        strategy=None,
        run_dir=rundir
    )
    return slurm_config


def load_config(workdir : str, benchmark_suite_config=None, benchmark_config_file_path=None):

    if benchmark_suite_config != None:

        if not isinstance(benchmark_suite_config, BenchmarkSuiteConfig) and not isinstance(benchmark_suite_config, dict):
            raise Exception("benchmark_suite_config must be either a BenchmarkSuiteConfig instance or a Python Dictionary")
        elif isinstance(benchmark_suite_config, BenchmarkSuiteConfig):
            benchmark_suite = benchmark_suite_config
        else:
            benchmark_suite = BenchmarkSuiteConfig(load_suite=benchmark_suite_config)
        return benchmark_suite
            
    elif benchmark_config_file_path != None:

        if not isinstance(benchmark_config_file_path, str):
            raise Exception("benchmark_config_file_path must be a string")
        else:
            return BenchmarkSuiteConfig(file_path=benchmark_config_file_path, file_dir=None, overwrite=False)

    else:
        raise Exception("Either a BenchmarkSuiteConfig instance or a configuration file must be an input")