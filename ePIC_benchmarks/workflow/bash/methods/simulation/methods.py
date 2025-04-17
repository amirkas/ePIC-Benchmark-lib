from parsl import AUTO_LOGNAME
from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.container.containers import ContainerUnion
from typing import Optional
from ePIC_benchmarks.workflow.bash.utils import concatenate_commands, source_epic_command, change_directory_command

def run_npsim(
        workflow_config : WorkflowConfig,
        benchmark_name : str,
        simulation_name : str,
        container : Optional[ContainerUnion] = None,
        stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME,
        **kwargs) -> str:

    source_command = source_epic_command(workflow_config, benchmark_name)
    temp_dir = workflow_config.paths.simulation_instance_temp_dir_path(benchmark_name, simulation_name)
    change_temp_dir_cmd = change_directory_command(temp_dir)
    npsim_command = workflow_config.executor.npsim_command_string(
        benchmark_name=benchmark_name,
        simulation_name=simulation_name, 
    )
    all_commands = concatenate_commands(change_temp_dir_cmd, source_command, npsim_command)
    if container is not None:
        all_commands = container.init_with_extra_commands(all_commands)
    return all_commands

def run_eicrecon(
        workflow_config : WorkflowConfig,
        benchmark_name : str,
        simulation_name : str,
        use_generated_material_map : bool = False,
        container : Optional[ContainerUnion] = None,
        stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME,
        **kwargs) -> str:
    
    if use_generated_material_map:
        material_map_path = workflow_config.paths.material_map_path(benchmark_name)
        if not material_map_path.exists():
            err = (
                "Material map path could not be found."
                "Generate one using the generate_material_map app"
            )
            raise RuntimeError(err)
        #Set the simulation's material_map_path
        workflow_config.simulation_config(benchmark_name, simulation_name).material_map_path = material_map_path

    source_command = source_epic_command(workflow_config, benchmark_name)
    temp_dir = workflow_config.paths.reconstruction_instance_temp_dir_path(benchmark_name, simulation_name)
    change_temp_dir_cmd = change_directory_command(temp_dir)
    eicrecon_command = workflow_config.executor.eicrecon_command_string(
        benchmark_name=benchmark_name,
        simulation_name=simulation_name, 
    )
    all_commands = concatenate_commands(change_temp_dir_cmd, source_command, eicrecon_command)
    if container is not None:
        all_commands = container.init_with_extra_commands(all_commands)
    return all_commands

