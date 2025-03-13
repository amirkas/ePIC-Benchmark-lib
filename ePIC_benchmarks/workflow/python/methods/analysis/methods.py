from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.analysis.performance import performance_plot

#Generates momentum resolution and track efficiency plots for a given benchmark + simulation configuration
def generate_performance_plots(workflow_config : WorkflowConfig, benchmark_name : str, simulation_name : str, **kwargs) -> str:

    analysis_dir = workflow_config.paths.analysis_out_dir_path(benchmark_name)
    recon_out_path = workflow_config.paths.reconstruction_out_file_path(benchmark_name, simulation_name)
    performance_plot(file_path=recon_out_path, output_dir=analysis_dir)


def momentum_resolution() -> str:

    pass


def tracking_efficiency() -> str:

    pass