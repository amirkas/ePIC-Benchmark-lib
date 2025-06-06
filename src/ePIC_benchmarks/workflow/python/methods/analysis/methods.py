from numpy import arange
from typing import Optional
from parsl import AUTO_LOGNAME

from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.analysis.performance import performance_plot

#Generates momentum resolution and track efficiency plots for a given benchmark + simulation configuration
def generate_performance_plots(
        workflow_config : WorkflowConfig, benchmark_name : str, simulation_name : str,
        analysis_dir_path : Optional[str] = None, plot_z_scores : bool = False,
        efficiency_eta_bins=arange(-4, 4.1, 0.5), resolution_eta_bins=arange(-4, 4.1, 0.5),
        kchain : int = 0, output_name : str = None,
        stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME,
        **kwargs
        ) -> str:

    analysis_dir = workflow_config.paths.analysis_out_dir_path(benchmark_name)
    recon_out_path = workflow_config.paths.reconstruction_out_file_path(benchmark_name, simulation_name)
    simulation_config = workflow_config.simulation_config(benchmark_name, simulation_name)
    performance_plot(
        file_path=recon_out_path,
        output_dir=analysis_dir,
        dir_path=analysis_dir_path,
        plot_resol_zscores=plot_z_scores,
        eff_eta_bins=efficiency_eta_bins,
        resol_eta_bins=resolution_eta_bins,
        kchain=kchain,
        output_name=output_name,
        simulation_config=simulation_config
    )

def momentum_resolution() -> str:

    pass


def tracking_efficiency() -> str:

    pass