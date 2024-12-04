from parsl import python_app, bash_app, join_app, AUTO_LOGNAME
from epic_benchmarks.workflow.workflow_manager import ParslWorkflowManager
import time

@python_app
def save_performance_plot(manager : ParslWorkflowManager, benchmark_name : str, simulation_name : str, future, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME):
    from epic_benchmarks.analysis.performance import performance_plot

    analysis_dir = manager.analysis_output_dir_path(benchmark_name)
    output_name = "{bench}_{sim}".format(bench=benchmark_name, sim=simulation_name)
    reconstruction_path = manager.reconstruction_output_file_path(benchmark_name, simulation_name)
    performance_plot(reconstruction_path, "", output_name, output_dir=analysis_dir)

    #Add analysis completed file for completion verification
    analysis_complete_path = manager.analysis_complete_file_path(benchmark_name, simulation_name)
    with open(analysis_complete_path, 'w') as analysis_file:
        analysis_file.write("analysis Complete!")
    
