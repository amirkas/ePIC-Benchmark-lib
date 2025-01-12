from dataclasses import dataclass
from typing import Optional, Union, Any

from pydantic import BaseModel, Field, field_validator
from parsl import bash_app, AUTO_LOGNAME

from epic_benchmarks.workflow import SUPPORTED_CONTAINERS, CONTAINER_MAP

@dataclass
class Container:

    pull_cmd_str : str
    init_container_cmd_str : str

    def pull_command(self, container_img : str):
        return f"{self.pull_cmd_str} {container_img}"

    def init_container(self, container_img : str, container_entry_command : Optional[str] = None):

        init_cmd = f"{self.init_container_cmd_str} {container_img}"
        if container_entry_command:
            init_cmd += f" {container_entry_command}"

        return init_cmd

    def commands_in_container(self, container_img : str, container_entry_command : Optional[str] = None, container_internal_cmds : Optional[str] = None):

        container_with_cmds = self.init_container(container_img, container_entry_command)
        if container_internal_cmds:
            container_with_cmds += f' "{container_internal_cmds}"'

        return container_with_cmds

class Shifter(Container):

    pull_cmd_str = "shifterimg pull"

class Docker(Container):

    pull_cmd_str = "docker image pull"



class ContainerCli(BaseModel):

    container : Union[Container, str]
    container_img : str
    container_entry_command : Optional[str] = Field(default=None)

    @field_validator('container')
    def validate_container(cls, value : Any):
        if isinstance(value, str):
            if value not in SUPPORTED_CONTAINERS:
                err = f"Container '{value}' is not a supported container type"
                raise ValueError(err)
            return CONTAINER_MAP[value]
        elif isinstance(value, Container):
            return value
        else:
            err = f"Could not parse '{value}' into a container"
            raise ValueError(err)

    def pull_command(self):

        return self.container.pull_command(self.container_img)

    def init_container(self):

        return self.container.init_container(self.container_img, self.container_entry_command)

    def commands_in_container(self, container_entry_command : Optional[str] = None):

        return self.container.commands_in_container(self.container_img, container_entry_command)


@bash_app
def pull_image(container_cli : ContainerCli):

    pull_cmd_str = container_cli.pull_command()
    return pull_cmd_str

