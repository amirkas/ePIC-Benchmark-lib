from parsl import AUTO_LOGNAME
from ePIC_benchmarks.container._base import BaseContainerConfig
from ePIC_benchmarks.workflow.bash.utils import concatenate_commands

#Pulls all provided containers into the environment
def pull_containers(*containers : BaseContainerConfig, **kwargs) -> str:

    pull_commands_lst = list(container.pull_command() for container in containers)
    concatenated_pull_commands = concatenate_commands(*pull_commands_lst)
    return concatenated_pull_commands

