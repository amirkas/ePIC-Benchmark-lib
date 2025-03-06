from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.analysis.performance import performance_plot




def all_performance_plots(workflow_config : WorkflowConfig, benchmark_name : str, *simulation_names : str, **kwargs) -> str:

    performance_plot()



def momentum_resolution() -> str:

    pass


def tracking_efficiency() -> str:

    pass