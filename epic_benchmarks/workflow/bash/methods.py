from pathlib import Path
from typing import Optional, Sequence
from parsl import AUTO_LOGNAME
from epic_benchmarks.workflow.config import WorkflowConfig
from epic_benchmarks.container._base import BaseContainerConfig
from epic_benchmarks.workflow.bash.utils import concatenate_commands

EPIC_REPO_URL = "https://github.com/eic/epic.git"

def pull_containers(*containers : BaseContainerConfig, stdout=AUTO_LOGNAME, stdin=AUTO_LOGNAME) -> str:

    pull_commands_lst = list(container.pull_command() for container in containers)
    concatenated_pull_commands = concatenate_commands(pull_commands_lst)
    return concatenated_pull_commands

def clone_epic(workflow_config : WorkflowConfig, benchmark_name : str, stdout=AUTO_LOGNAME, stdin=AUTO_LOGNAME) -> str:

    epic_directory_path = workflow_config.paths.epic_repo_path(benchmark_name)
    clone_command = f'git clone {EPIC_REPO_URL} "{epic_directory_path}"'
    return clone_command

def checkout_epic_branch(workflow_config : WorkflowConfig, benchmark_name : str, stdout=AUTO_LOGNAME, stdin=AUTO_LOGNAME) -> str:

    epic_directory_path = workflow_config.paths.epic_repo_path(benchmark_name)
    branch = workflow_config.executor.epic_branch(benchmark_name)
    checkout_command = f'git -C "{epic_directory_path}" checkout "{branch}"'
    return checkout_command

def compile_epic(workflow_config : WorkflowConfig, benchmark_name : str, num_threads : int = 1, stdout=AUTO_LOGNAME, stdin=AUTO_LOGNAME) -> str:

    epic_directory_path = workflow_config.paths.epic_repo_path(benchmark_name)
    change_directory_cmd = f'cd {epic_directory_path}'
    compile_pt_one_cmd = 'cmake --fresh -B build -S . -DCMAKE_INSTALL_PREFIX=install'
    compile_pt_two_cmd = f'cmake --build build -- install -j {num_threads}'
    all_commands = concatenate_commands(change_directory_cmd, compile_pt_one_cmd, compile_pt_two_cmd)
    return all_commands

def run_npsim(workflow_config : WorkflowConfig, benchmark_name : str, simulation_name : str, stdout=AUTO_LOGNAME, stdin=AUTO_LOGNAME) -> str:

    npsim_command = workflow_config.executor.npsim_command_string(
        benchmark_name=benchmark_name,
        simulation_name=simulation_name, 
    )
    return npsim_command

def run_eicrecon(workflow_config : WorkflowConfig, benchmark_name : str, simulation_name : str, stdout=AUTO_LOGNAME, stdin=AUTO_LOGNAME) -> str:
    
    eicrecon_command = workflow_config.executor.eicrecon_command_string(
        benchmark_name=benchmark_name,
        simulation_name=simulation_name, 
    )
    return eicrecon_command

