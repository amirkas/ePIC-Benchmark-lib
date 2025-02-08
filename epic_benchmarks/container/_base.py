from abc import ABC, abstractmethod
from typing import Literal, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, SerializationInfo, model_serializer


class BaseContainerConfig(BaseModel, ABC):

    container_type : Literal["Base"] = "Base"

    @abstractmethod
    def pull_command(self) -> str:
        pass

    @abstractmethod
    def init_command(self) -> str:
        pass

    @abstractmethod
    def init_with_extra_commands(self, *extra_commands : str) -> str:
        pass

    @model_serializer(mode='wrap')
    def serialize_container_config(self, handler, info : SerializationInfo) -> Dict[str, Any]:

        serialized_dict = {}
        for field_name in self.model_fields:
            field_data = getattr(self, field_name, None)
            serialized_dict[field_name] = field_data

        return serialized_dict







