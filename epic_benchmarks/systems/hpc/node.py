from typing import Self, Union
from pydantic import BaseModel, field_validator

NumberType = Union[int, float]

class BaseSystemNode(BaseModel):

    available_cpu_cores : int
    available_gpu_cores : int = 0
    available_ram : float
    available_vram : float = 0
    cpu_multiplicative : bool = False
    gpu_multiplicative : bool = False
    ram_multiplicative : bool = False
    vram_multiplicative : bool = False

    def __add__(self, other : Self) -> Self:

        class_type = self.__class__
        new_cpu_cores = self.available_cpu_cores + other.available_cpu_cores
        new_gpu_cores = self.available_gpu_cores + other.available_gpu_cores
        return class_type(
            available_cpu_cores=new_cpu_cores,
            available_gpu_cores=new_gpu_cores,
            available_ram=self.available_ram,
            available_vram=self.available_vram,
        )

    def __sub__(self, other : Self) -> Self:
        class_type = self.__class__
        new_cpu_cores = self.available_cpu_cores - other.available_cpu_cores
        new_gpu_cores = self.available_gpu_cores - other.available_gpu_cores
        return class_type(
            available_cpu_cores=new_cpu_cores,
            available_gpu_cores=new_gpu_cores,
            available_ram=self.available_ram,
            available_vram=self.available_vram,
        )

    def __mul__(self, other : NumberType) -> Self:

        class_type = self.__class__
        new_cpu_cores = self.available_cpu_cores
        new_gpu_cores = self.available_gpu_cores
        new_ram = self.available_ram
        new_vram = self.available_vram
        if self.cpu_multiplicative:
            new_cpu_cores = int(new_cpu_cores * other)
        if self.gpu_multiplicative:
            new_gpu_cores = int(new_gpu_cores * other)
        if self.ram_multiplicative:
            new_ram = int(new_ram * other)
        if self.vram_multiplicative:
            new_vram = int(new_vram * other)

        return class_type(
            available_cpu_cores=new_cpu_cores,
            available_gpu_cores=new_gpu_cores,
            available_ram=new_ram,
            available_vram=new_vram,
        )

    def __truediv__(self, other : NumberType) -> Self:

        return self.__mul__(1 / other)

    @field_validator('available_cpu_cores', 'available_gpu_cores', mode='after')
    def validate_cores_exists(cls, cores):
        if cores < 0:
            raise ValueError("Number of cores must be positive")
        return cores

    @field_validator('available_ram', 'available_vram', mode='after')
    def validate_ram_exists(cls, ram):
        if ram < 0:
            raise ValueError("RAM (GB) must be positive")
        return ram


