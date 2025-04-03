from dataclasses import dataclass, is_dataclass
from pydantic import BaseModel, ConfigDict, Field, model_serializer, SerializationInfo
from pydantic.main import IncEx
from typing import TYPE_CHECKING, Dict, Any, Optional, Type, Union, TypeVar, Literal, ClassVar
from parsl.dataflow.dependency_resolvers import DependencyResolver
import logging
logger = logging.getLogger(__name__)

SERIALIZATION_OPTIONS = {'dict', 'config'}
ParslConfigType = TypeVar("ParslConfigType")

class BaseParslModel(BaseModel):

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        strict=False,
        validate_default=True,
    )
    config_type_name : str = Field(init=False)
    config_type : ClassVar[Type] = Field(init=False, exclude=True)

    def to_parsl_config(self, exclude : Optional[str] = None, *excludes):

        exclude_lst = []
        if exclude is not None:
            exclude_lst.append(exclude)
        if excludes is not None:
            for exclude_str in excludes:
                exclude_lst.append(exclude_str)
        if len(exclude_lst) > 0:
            return self.model_dump(exclude=set(exclude_lst), exclude_defaults=False, context={'option' : 'config'})
        else:
            return self.model_dump(exclude_defaults=False, context={'option' : 'config'})
                

    @model_serializer(mode='wrap')
    def with_option_serializer(self, handler, info : SerializationInfo) -> Union[Dict[str, Any], ParslConfigType]:

        option = 'dict'
        context = info.context
        if context:
            option = context.get('option', 'dict')
        result = handler(self)
        assert(isinstance(result, dict))
        if option == 'dict':

            return {key : value for key, value in result.items() if (key in self.model_fields_set or key == 'config_type_name')}
        
        elif option == 'config':

            #Remove config_type_name from result
            result.pop('config_type_name', None)

            if "dependency_resolver" in result.keys() and isinstance(result["dependency_resolver"], dict):
                result['dependency_resolver'] = DependencyResolver(**result['dependency_resolver'])

            as_config = self.config_type(**result)
            return as_config
        
        else:
            err = f"Option '{option}' is not valid. Valid options are {", ".join(SERIALIZATION_OPTIONS)}"
            raise ValueError(err)

    if TYPE_CHECKING:
        #Ensure type checkers see correct return type
        def model_dump(
            self,
            *,
            mode: Literal['json', 'python'] | str = 'python',
            include: IncEx | None = None,
            exclude: IncEx | None = None,
            context: Any | None = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal['none', 'warn', 'error'] = True,
            serialize_as_any: bool = False,
        ) -> Union[Dict[str, Any], ParslConfigType]: ...


