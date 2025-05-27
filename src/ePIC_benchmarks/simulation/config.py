
from pathlib import Path
from pydantic import (
    BaseModel, field_serializer, field_validator,
    model_serializer, ConfigDict, Field, AliasPath,
    AliasChoices
)
from pydantic_core.core_schema import ValidationInfo
from typing import Dict, Union, Optional, Any
from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks._file.utils import absolute_path

from ePIC_benchmarks.simulation.simulation_types import Particle, Momentum, Angle, Eta
from ePIC_benchmarks.simulation._bash import NpsimModel, EicreconModel
from ePIC_benchmarks.simulation._distribution.config import DistributionSettings
from ePIC_benchmarks.simulation._utils import validate_enum, _generate_file_name
import ePIC_benchmarks.simulation._validators as simulation_validator

DistributionTypes = Union[Angle, Eta]

ROOT_FILE_SUFFIX = ".root"
NPSIM_OUTPUT_FILE_PREFIX = "npsim_"
EICRECON_OUTPUT_FILE_PREFIX = "eicrecon_"

class SimulationBase(BaseModel):

    model_config = ConfigDict(validate_assignment=True, validate_default=True, populate_by_name=True)

    num_events : int = Field(description="Number of events to simulate")
    momentum_min : Momentum = Field(
            validation_alias=AliasChoices(
                'momentum',
                'momentum_min',
                'min_momentum',
                AliasPath('momentum_range', 0),
                AliasPath('momenta', 0)
            ),
            description="Minimum momentum value (or static momentum value)",
    )
    momentum_max : Momentum = Field(
        validation_alias=AliasChoices(
            'momentum',
            'momentum_max',
            'max_momentum',
            AliasPath('momentum_range', 0),
            AliasPath('momenta', 0)
        ),
        description="Maximum momentum value (or static momentum value)",
    )
    name : Optional[str] = Field(default=None, description="Name of the simulation")
    enable_gun : bool = Field(default=True)
    particle : Union[str, Particle] = Field(default=Particle.PionNeutral)
    multiplicity : float = Field(default=1.0)
    detector_xml : Path = Field(exclude=False)
    use_material_map : bool = False
    material_map_path : Optional[PathType] = Field(default=None, init=False)

class SimulationConfig(SimulationBase, DistributionSettings):

    model_config = ConfigDict(validate_assignment=True, validate_default=True, populate_by_name=True)

    #Generates the npsim command for a Simulation Config instance
    def npsim_cmd(self, output_dir_path : PathType, epic_repo_path : Optional[PathType]=None,):
        
        dumped_self = self.model_dump(exclude_none=True)
        dumped_self["detector_path"] = self._abs_detector_path(epic_repo_path)
        dumped_self["output_path"] = self._abs_npsim_output_path(output_dir_path)
        npsim_model = NpsimModel(**dumped_self)
        return npsim_model.generate_command()

    #Generates the eicrecon command for a Simulation Config instance
    def eicrecon_cmd(self, output_dir_path : PathType, input_dir_path : PathType, epic_repo_path : Optional[PathType]=None):

        dumped_self = self.model_dump(exclude_none=True)
        dumped_self["detector_path"] = self._abs_detector_path(epic_repo_path)
        dumped_self["output_path"] = self._abs_eicrecon_output_path(output_dir_path)
        dumped_self["input_path"] = self._abs_eicrecon_input_path(input_dir_path)
        eicrecon_model = EicreconModel(**dumped_self)
        return eicrecon_model.generate_command()    

    #Returns the absolute path to a Simulation Config instance's detector build file
    #using the provided path to the ePIC repository
    def _abs_detector_path(self, epic_repo_path : Optional[PathType]):

        relative_detective_build_path = Path('install', 'share', 'epic')
        relative_detector_path = relative_detective_build_path.joinpath(self.detector_xml)
        return absolute_path(relative_detector_path, epic_repo_path)
    
    #Returns the absolute path to a Simulation Config instance's npsim output root file
    def _abs_npsim_output_path(self, output_dir : PathType):

        return absolute_path(self.npsim_filename, output_dir)
    
    #Returns the absolute path to a Simulation Config instance's eicrecon output root file
    def _abs_eicrecon_output_path(self, output_dir : PathType):

        return absolute_path(self.eicrecon_filename, output_dir)
    
    #Returns the absolute path to a Simulation Config instance's eicrecon input root file
    #NOTE: This will always be the output path of the npsim output root file
    def _abs_eicrecon_input_path(self, input_dir : PathType):

        return self._abs_npsim_output_path(input_dir)

    #Generates the name for the npsim output root file
    @property
    def npsim_filename(self):
        return _generate_file_name(self.name, NPSIM_OUTPUT_FILE_PREFIX, ROOT_FILE_SUFFIX)
    
    #Generates the name for the eicrecon output root file
    @property
    def eicrecon_filename(self):
        return _generate_file_name(self.name, EICRECON_OUTPUT_FILE_PREFIX, ROOT_FILE_SUFFIX)

    #Validates whether raw momentum input is valid, and parses it into a Momentum instance
    @field_validator('momentum_min', 'momentum_max', mode='before')
    def validate_momentum_limits(cls, momentum_limit : Any) -> Momentum:
        try:
            return Momentum.to_quantity(momentum_limit)
        except Exception as e:
            raise e
        
    #Validates a given name, or generates a name from momentum and distribution fields
    @field_validator('name', mode='after')
    def validate_name(cls, name : Any, validation_info : ValidationInfo) -> str:
        
        try:
            momentum_min = validation_info.data["momentum_min"]
            momentum_max = validation_info.data["momentum_max"]
            distribution_type = validation_info.data["distribution_type"]    
            distribution_min = validation_info.data["distribution_min"]
            distribution_max = validation_info.data["distribution_max"]

            return simulation_validator.validate_name(
                name_value=name,
                momentum_min=momentum_min,
                momentum_max=momentum_max,
                distribution_type=distribution_type,
                distribution_min=distribution_min,
                distribution_max=distribution_max
            )
        except Exception as e:
            raise e
    
    #Checks if num events is greater than 0
    @field_validator('num_events', mode='after')
    def check_valid_num_events(cls, number_of_events : int) -> int:
        try:
            simulation_validator.validate_num_events(number_of_events)
        except Exception as e:
            raise e
        return number_of_events

    #Checks whether the provided particle is valid and casts it if necessary.
    @field_validator('particle', mode='before')
    def validate_particle(cls, particle : Union[str, Particle]) -> str:
        try:
            return validate_enum(particle, Particle)
        except Exception as e:
            raise e

    #Checks if multiplicity is greater than 0
    @field_validator('multiplicity', mode='after')
    def check_valid_multiplicity(cls, multiplicity : float) -> float:
        try:
            simulation_validator.validate_multiplicity(multiplicity)
        except Exception as e:
            raise e
        return multiplicity
    
    #Serializes a particle to a string format
    @field_serializer('particle')
    def serialize_particle(cls, particle : Union[str, Particle]) -> str:
        if isinstance(particle, Particle):
            return particle.value
        else:
            return particle

    #Custom model serializer
    @model_serializer(mode='wrap')
    def simulation_model_serializer(self, handler) -> Dict[str, Any]:

        serialized_dict : Dict[str, Any] = {"name": self.name, "num_events": self.num_events}
        if self.momentum_min == self.momentum_max:
            serialized_dict["momentum"] = str(self.momentum_min)
        else:
            serialized_dict["momentum_min"] = str(self.momentum_min)
            serialized_dict["momentum_max"] = str(self.momentum_max)

        serialized_dict['distribution_type'] = str(self.distribution_type.value)
        if self.theta_min is not None and self.theta_max is not None:
            serialized_dict["theta_min"] = str(self.theta_min)
            serialized_dict["theta_max"] = str(self.theta_max)
        elif self.eta_min is not None and self.eta_max is not None:
            serialized_dict["eta_min"] = str(self.eta_min)
            serialized_dict["eta_max"] = str(self.eta_max)
        #TODO: Add serialization for supported distributions in the future.

        serialized_dict["enable_gun"] = self.enable_gun
        serialized_dict["particle"] = str(self.particle.value)
        serialized_dict["multiplicity"] = self.multiplicity
        serialized_dict["detector_xml"] = str(self.detector_xml)
        if self.material_map_path is not None:
            serialized_dict["material_map_path"] = str(self.material_map_path)
        if self.use_material_map:
            serialized_dict["use_material_map"] = self.use_material_map

        return serialized_dict


