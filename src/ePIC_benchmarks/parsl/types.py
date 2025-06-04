
from typing import Union
from parsl.dataflow.futures import AppFuture as AppFuture
from parsl.app.futures import DataFuture as DataFuture

FutureType = Union[AppFuture, DataFuture]