

from typing import Optional, ClassVar, Sequence
from pydantic import BaseModel, Field
from epic_benchmarks.systems.hpc.node import BaseSystemNode


NodeList = Sequence[BaseSystemNode]

class SlurmQOS(BaseModel):

    name : ClassVar[str]
    max_nodes : ClassVar[NodeList]
    min_walltime: ClassVar[str] = Field(default="00:00:00", pattern=r"^(\d[2]):(\d[2]):(\d[2])$")
    max_walltime : ClassVar[str] = Field(default="99:59:59", pattern=r"^(\d[2]):(\d[2]):(\d[2])$")
    shared : ClassVar[bool]






    