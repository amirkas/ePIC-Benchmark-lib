

from typing import Optional
from pydantic import BaseModel, Field, constr



class QOS(BaseModel):

    name : str
    cpu_cores_per_node : Optional[int] = None
    gpus_per_node : Optional[int] = None
    min_walltime : constr = Field(regex="^(\d[2]):(\d[2]):(\d[2])$", default="99:59:59")
    max_walltime : constr = Field(regex="^(\d[2]):(\d[2]):(\d[2])$", default="00:00:00")
    shared : bool = False

    