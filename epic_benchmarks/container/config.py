
from functools import cached_property
from typing import Self, Union, Any
from pydantic import BaseModel, ValidationError, field_serializer, field_validator, model_validator

from epic_benchmarks.container.containers import BaseContainer, Containers

class ContainerConfig(BaseModel):

    container : Union[str, BaseContainer]
    image : str 

    @field_validator('container', mode='before')
    def validate_container(cls, container_value : Any) -> BaseContainer:

        if isinstance(container_value, BaseContainer):
            return container_value
        elif isinstance(container_value, str): 
            try:
                container_object = Containers[container_value]
                return container_object
            except:
                err = f"'{container_value}' is not a valid container."
                raise ValidationError(err)
        else:
            err = f"Container must be a string or an instance of BaseContainer. Got type '{type(container_value)}'"
            raise ValueError(err)

    @model_validator(mode='after')
    def validate_image(self) -> Self:

        #TODO: Validate that provided image is valid for provided container
        return self
    
    @field_serializer('container')
    def serialize_container(cls, container_value : Union[str, BaseContainer]) -> str:

        if isinstance(container_value, BaseContainer):
            return container_value.name
        else:
            return container_value
        
    @cached_property
    def pull_command(self) -> str:

        assert(isinstance(self.container), BaseContainer)
        return self.container.pull_command(self.image)
    
    @cached_property
    def init_command(self) -> str:

        assert(isinstance(self.container), BaseContainer)
        return self.container.init_container_command(self.image)

    def containerize_command(self, command : str):
        return self.container.containerize_commands(self.image, command)