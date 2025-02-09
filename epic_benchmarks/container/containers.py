from typing import Literal, Optional, Union, Literal, Annotated
from epic_benchmarks.container._base import BaseContainerConfig
from pydantic import TypeAdapter, Field

class DockerConfig(BaseContainerConfig):

    container_type : Literal["Docker"] = "Docker"
    image : Optional[str] = None

    def pull_command(self) -> str:

        if self.image is None:
            return ""
        return f"docker image pull {self.image}"

    def init_command(self) -> str:

        return f"docker build -t {self.image}; docker init"
    
    def init_with_extra_commands(self, *extra_commands) -> str:
        return ""


class ShifterConfig(BaseContainerConfig):

    image : str
    container_type : Literal["Shifter"] = "Shifter"
    entry_point : str = ""
    entry_command : str = ""

    def pull_command(self) -> str:

        return f'shifterimg pull {self.image}'

    def init_command(self) -> str:

        if len(self.entry_command) > 0:
            return f'shifter --image={self.image} {self.entry_point} "{self.entry_command}"'
        else:
            return f'shifter --image={self.image} {self.entry_point}'

    def init_with_extra_commands(self, *extra_commands : str) -> str:

        extra_commands = ";".join([cmd for cmd in extra_commands])
        if len(self.entry_command) > 0:
            return f'shifter --image={self.image} {self.entry_point} "{self.entry_command}{extra_commands}"'
        else:
            return f'shifter --image={self.image} {self.entry_point} "{extra_commands}"'


ContainerUnion = Union[DockerConfig, ShifterConfig]
ContainerConfigAdapter : TypeAdapter[ContainerUnion] = TypeAdapter(Annotated[ContainerUnion, Field(discriminator='container_type')])

