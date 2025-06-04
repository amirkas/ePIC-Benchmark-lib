from concurrent.futures import Future
from typing import Union, Sequence

WorkflowFuture = Union[Future, Sequence[Future]]

__all__ = ['WorkflowFuture']