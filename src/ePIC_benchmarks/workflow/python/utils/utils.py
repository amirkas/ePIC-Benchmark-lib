from ePIC_benchmarks.workflow import WorkflowConfig
from ePIC_benchmarks.simulation import SimulationConfig

#Returns all the eta bins for a benchmark configuration
def get_eta_bins(workflow_config : WorkflowConfig, benchmark_name : str, *simulation_names : str):

    all_bins = []
    for sim_name in simulation_names:
        sim_config = workflow_config.simulation_config(benchmark_name, sim_name)
        curr_bin = (sim_config.eta_min, sim_config.eta_max)
        all_bins.append(curr_bin)

    return all_bins

