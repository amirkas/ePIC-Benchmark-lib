from parsl import AUTO_LOGNAME
from epic_benchmarks.workflow.config import WorkflowConfig
from epic_benchmarks.workflow.bash.utils import concatenate_commands, source_epic_command, change_directory_command

def run_npsim(workflow_config : WorkflowConfig, benchmark_name : str, simulation_name : str, **kwargs) -> str:


    source_command = source_epic_command(workflow_config, benchmark_name)
    temp_dir = workflow_config.paths.simulation_instance_temp_dir_path(benchmark_name, simulation_name)
    change_temp_dir_cmd = change_directory_command(temp_dir)
    npsim_command = workflow_config.executor.npsim_command_string(
        benchmark_name=benchmark_name,
        simulation_name=simulation_name, 
    )
    all_commands = concatenate_commands(change_temp_dir_cmd, source_command, npsim_command)
    return all_commands

def run_eicrecon(workflow_config : WorkflowConfig, benchmark_name : str, simulation_name : str, **kwargs) -> str:
    
    source_command = source_epic_command(workflow_config, benchmark_name)
    temp_dir = workflow_config.paths.reconstruction_instance_temp_dir_path(benchmark_name)
    change_temp_dir_cmd = change_directory_command(temp_dir)
    eicrecon_command = workflow_config.executor.eicrecon_command_string(
        benchmark_name=benchmark_name,
        simulation_name=simulation_name, 
    )
    all_commands = concatenate_commands(change_temp_dir_cmd, source_command, eicrecon_command)
    return all_commands

