from parsl.dataflow.dependency_resolvers import (
    DependencyResolver, deep_traverse_to_gather, deep_traverse_to_unwrap,
    shallow_traverse_to_gather, shallow_traverse_to_unwrap)
from pydantic import ConfigDict, Field, BaseModel
from concurrent.futures import Future

from ePIC_benchmarks.parsl._base import BaseParslModel
from typing import Literal, Callable, Sequence, ClassVar, Type, Any, Union, Dict

class ParslDependencyResolver(BaseModel):

    model_config = ConfigDict(validate_default=True, strict=True, arbitrary_types_allowed=True)

    config_type : ClassVar[Type] = DependencyResolver

    traverse_to_gather: Callable[[object], Sequence[Future]] = Field(default=deep_traverse_to_gather)
    traverse_to_unwrap: Callable[[object], object] = Field(default=deep_traverse_to_unwrap)

DEEP_DEPENDENCY_RESOLVER = ParslDependencyResolver(traverse_to_gather=deep_traverse_to_gather,
                                              traverse_to_unwrap=deep_traverse_to_unwrap)

SHALLOW_DEPENDENCY_RESOLVER = ParslDependencyResolver(traverse_to_gather=shallow_traverse_to_gather,
                                                 traverse_to_unwrap=shallow_traverse_to_unwrap)

def dependency_resolver_serializer(value : Any, handler, info) -> Union[Dict[str, Any], DependencyResolver]:

    partial_result = handler(value, info)
    context = info.context
    option = 'dict'
    if context:
        option = context.get('option', 'dict')
    if option == 'dict':
        return partial_result
    elif option == 'config':
        return DependencyResolver(**partial_result)
    else:
        err = f"{option} is not a valid serialization option"
        raise ValueError(err)

