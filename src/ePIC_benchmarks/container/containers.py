from typing import Literal, Optional, Union, Literal, Annotated
from ePIC_benchmarks.container._base import BaseContainerConfig
from pydantic import TypeAdapter, Field

#Container Configuration for Docker Containers
class DockerConfig(BaseContainerConfig):

    container_type : Literal["Docker"] = "Docker"
    image : Optional[str] = None

    #Returns the string format for the command to pull the container
    def pull_command(self) -> str:

        if self.image is None:
            return ""
        return f"docker image pull {self.image}"

    #Returns the string format to initialize the container
    def init_command(self) -> str:

        return f"docker build -t {self.image}; docker init"
    
    #Returns the string format to initialize the container with
    #extra commands to be executed inside the container.
    def init_with_extra_commands(self, *extra_commands) -> str:
        return ""

#Container Configuration for Shifter Containers
class ShifterConfig(BaseContainerConfig):

    image : str
    container_type : Literal["Shifter"] = "Shifter"
    entry_point : str = ""
    entry_command : str = ""

    #Returns the string format for the command to pull the container
    def pull_command(self) -> str:

        return f'shifterimg pull {self.image}'

    #Returns the string format to initialize the container
    def init_command(self) -> str:

        if len(self.entry_command) > 0:
            return f'shifter --image={self.image} {self.entry_point} "{self.entry_command}"'
        else:
            return f'shifter --image={self.image} {self.entry_point}'

    #Returns the string format to initialize the container with
    #extra commands to be executed inside the container.
    def init_with_extra_commands(self, *extra_commands : str) -> str:

        extra_commands = ";".join([cmd for cmd in extra_commands])
        if len(self.entry_command) > 0:
            return f'shifter --image={self.image} {self.entry_point} "{self.entry_command}{extra_commands}"'
        else:
            return f'shifter --image={self.image} {self.entry_point} "{extra_commands}"'


#TODO: Add other container configurations (Like singularity)

ContainerUnion = Union[DockerConfig, ShifterConfig]
ContainerConfigAdapter : TypeAdapter[ContainerUnion] = TypeAdapter(Annotated[ContainerUnion, Field(discriminator='container_type')])

