from typing import Literal
from epic_benchmarks.container._base import BaseContainerConfig

class DockerConfig(BaseContainerConfig):

    container_type : Literal["Docker"] = "Docker"

    def pull_command(self) -> str:

        return f"docker image pull {self.image}"

    def init_command(self) -> str:

        return f"docker build -t {self.image}; docker init"


class ShifterConfig(BaseContainerConfig):

    container_type : Literal["Shifter"] = "Shifter"
    entry_point : str = ""

    def pull_command(self) -> str:

        return f"shifterimg pull {self.image}"

    def init_command(self) -> str:

        return f"shifter --image={self.image} {self.entry_point}"



# @dataclass
# class BaseContainer:
#
#     name : str
#     pull_cmd_str : str
#     init_container_cmd_str : str
#
#     def pull_command(self, container_img : str):
#         return f"{self.pull_cmd_str} {container_img}"
#
#     def init_container_command(self, container_img : str, container_entry_command : Optional[str] = None):
#
#         init_cmd = f"{self.init_container_cmd_str} {container_img}"
#         if container_entry_command:
#             init_cmd += f" {container_entry_command}"
#
#         return init_cmd
#
#     def containerize_commands(self, container_img : str, container_entry_command : Optional[str] = None, container_internal_cmds : Optional[str] = None):
#
#         container_with_cmds = self.init_container(container_img, container_entry_command)
#         if container_internal_cmds:
#             container_with_cmds += f' "{container_internal_cmds}"'
#
#         return container_with_cmds
#
# class DockerContiner(BaseContainer):
#
#     name = "Docker"
#     pull_cmd_str = "docker image pull"
#
# class ShifterContainer(BaseContainer):
#
#     name = "Shifter"
#     pull_cmd_str = "shifterimg pull"
#
# class Containers(Enum):
#
#     def __new__(cls, string_value : str, container_object : BaseContainer):
#
#         new_obj = object.__new__(cls)
#         new_obj._value_ = string_value
#         new_obj.container_obj = container_object
#         return new_obj
#
#     Docker = ("Docker", DockerContiner)
#     Shifter = ("Shifter", ShifterContainer)
    