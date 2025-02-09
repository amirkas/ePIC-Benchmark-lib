from parsl import AUTO_LOGNAME
from epic_benchmarks.container._base import BaseContainerConfig
from epic_benchmarks.workflow.bash.utils import concatenate_commands

def pull_containers(*containers : BaseContainerConfig, inputs=[], outputs=[], stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME) -> str:

    pull_commands_lst = list(container.pull_command() for container in containers)
    concatenated_pull_commands = concatenate_commands(*pull_commands_lst)
    return concatenated_pull_commands

