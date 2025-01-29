import os
from epic_benchmarks.configs import SimulationConfig, BenchmarkConfig, WorkflowConfig
from epic_benchmarks.parsl import ParslConfig, HighThroughputExecutorConfig, SlurmProviderConfig, SrunLauncherConfig
from epic_benchmarks.workflow import run_from_file_path

simulation_configuration = SimulationConfig(
    num_events=1000,
    momentum="10GeV",
    detector_relative_path="relative/test/path.xml",
    distribution_type="eta",
    eta_min=0.0,
    eta_max=1.0,
)

benchmark_configuration = BenchmarkConfig(
    epic_branch="main",
    simulation_configs=[simulation_configuration],
)

parsl_configuration = ParslConfig(
    executors=[
        HighThroughputExecutorConfig(
            provider=SlurmProviderConfig(
                launcher=SrunLauncherConfig(overrides="-c 8"),
                account="test_account",
                walltime="00:10:00",
                max_blocks=1,
            ),
            cpu_affinity='block'
        )
    ],
)

workflow_configuration = WorkflowConfig(
    benchmarks=[benchmark_configuration],
    parsl_config=parsl_configuration
)

workflow_configuration.save("slurm_workflow_config.yaml")

file_path = os.path.join(os.getcwd(), "slurm_workflow_config.yaml")
script_path = os.path.join(os.getcwd(), "workflow.py")
run_from_file_path(file_path, script_path)

