from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

class BaseContainerConfig(BaseModel, ABC):

    container_type : str = Field(init=False)

    image : str
    entry_command : str

    @abstractmethod
    def pull_command(self) -> str:
        pass

    @abstractmethod
    def init_command(self) -> str:
        pass

    def init_with_extra_command(self, *extra_commands : str) -> str:

        extra_str = "; ".join(extra_commands)
        if len(extra_str) == 0:
            return self.init_command()
        return f'{self.init_command()} "{extra_str}"'