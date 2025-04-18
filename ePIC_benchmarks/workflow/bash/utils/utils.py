from typing import Sequence 
from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks.workflow.config import WorkflowConfig

#Concatenates multiple bash commands
def concatenate_commands(*commands : Sequence[str]):

    return ';'.join(commands)

#Returns the command that sources the ePIC repository for the current process
def source_epic_command(workflow_config : WorkflowConfig, benchmark_name : str) -> str:
    epic_directory_path = workflow_config.paths.epic_repo_path(benchmark_name)
    install_script_path = epic_directory_path.joinpath('install', 'bin', 'thisepic.sh')
    source_command = f'source {install_script_path}'
    return source_command

#Returns the command that changes the current working directory to the provided path
def change_directory_command(path : PathType):

    return f'cd {path}'
