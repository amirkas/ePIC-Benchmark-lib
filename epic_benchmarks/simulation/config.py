
from pathlib import Path

from pydantic import BaseModel, field_serializer, field_validator, model_serializer, ConfigDict
from typing import Dict, Union, Optional, Any

from pydantic_core.core_schema import ValidationInfo

from epic_benchmarks.simulation.types import Particle, Momentum, Angle, Eta
from epic_benchmarks._bash.flags import BashExecFlag
from epic_benchmarks._file.types import PathType
import epic_benchmarks.simulation._validators as simulation_validator

from epic_benchmarks.simulation._fields import SimulationSettingsFields
from epic_benchmarks.simulation.distribution.config import DistributionSettings
from epic_benchmarks.simulation.filepaths.config import SimulationFilePaths

NPSIM_METADATA_KEY = "npsim"
EICRECON_METADATA_KEY = "eicrecon"

DistributionTypes = Union[Angle, Eta]

def _generate_command(settings_model : BaseModel, flag_metadata_key : str, program_cmd : str):

    all_flags_str = _generate_flags_string(settings_model, flag_metadata_key)
    return f"{program_cmd}{all_flags_str}"

def _generate_flags_string(settings_model : BaseModel, flag_metadata_key : str):

    flag_str = ""
    for field_name, field_info in settings_model.model_fields.items():

        field_val = getattr(settings_model, field_name, None)
        if isinstance(field_val, BaseModel):
            nested_flag_str = _generate_flags_string(field_val, flag_metadata_key)
            flag_str += " " + nested_flag_str
        if not field_info or not field_info.json_schema_extra:
            continue
        if flag_metadata_key in field_info.json_schema_extra.keys():
            field_flag = field_info.json_schema_extra[flag_metadata_key]
            assert isinstance(field_flag, BashExecFlag)
            if field_val:
                formatted_flag = field_flag.bash_format(field_val)
                flag_str += " " + formatted_flag
    return flag_str

class SimulationBase(BaseModel):

    num_events : int = SimulationSettingsFields.NUM_EVENTS_FIELD.value
    momentum_min : Momentum = SimulationSettingsFields.MOMENTUM_MIN_FIELD.value
    momentum_max : Momentum = SimulationSettingsFields.MOMENTUM_MAX_FIELD.value
    name : Optional[str] = SimulationSettingsFields.NAME_FIELD.value
    enable_gun : bool = SimulationSettingsFields.ENABLE_GUN_FIELD.value
    particle : Union[str, Particle] = SimulationSettingsFields.PARTICLE_FIELD.value
    multiplicity : float = SimulationSettingsFields.MULTIPLICITY_FIELD.value
    detector_relative_path : Path = SimulationSettingsFields.DETECTOR_FILE_RELATIVE_PATH_FIELD.value
    file_paths : Optional[SimulationFilePaths] = SimulationSettingsFields.FILE_PATHS_FIELD.value



class SimulationConfig(SimulationBase, DistributionSettings):

    model_config = ConfigDict(validate_assignment=True, validate_default=True)

    def npsim_cmd(self, epic_repo_path : Optional[PathType]=None, output_dir_path : Optional[PathType]=None):
        
        file_paths_model = SimulationFilePaths.construct_file_paths_model(
            simulation_name=self.name,
            detector_build_relative_path=self.detector_relative_path,
            epic_repository_path=epic_repo_path,
            simulation_output_dir_path=output_dir_path
        )
        
        self.file_paths = file_paths_model
        return _generate_command(self, NPSIM_METADATA_KEY, "npsim")

    def eicrecon_cmd(self, epic_repo_path : Optional[PathType]=None, input_dir_path : Optional[PathType]=None, output_dir_path : Optional[PathType]=None):

        file_paths_model = SimulationFilePaths.construct_file_paths_model(
            simulation_name=self.name,
            detector_build_relative_path=self.detector_relative_path,
            epic_repository_path=epic_repo_path,
            simulation_output_dir_path=input_dir_path,
            reconstruction_output_dir_path=output_dir_path
        )
        
        self.file_paths = file_paths_model
        return _generate_command(self, EICRECON_METADATA_KEY, "eicrecon")

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
            err = f"Keys : {validation_info.data}"
            raise ValueError(err)
    
    #Checks if num events is greater than 0
    @field_validator('num_events', mode='after')
    def check_valid_num_events(cls, number_of_events : int) -> int:
        try:
            simulation_validator.validate_num_events(number_of_events)
        except Exception as e:
            raise e
        return number_of_events

    #Checks if multiplicity is greater than 0
    @field_validator('multiplicity', mode='after')
    def check_valid_multiplicity(cls, multiplicity : float) -> float:
        try:
            simulation_validator.validate_multiplicity(multiplicity)
        except Exception as e:
            raise e
        return multiplicity
    
    @field_serializer('particle')
    def serialize_particle(cls, particle : Union[str, Particle]) -> str:
        if isinstance(particle, Particle):
            return particle.value
        else:
            return particle

    #Custom model serializer
    @model_serializer(mode='wrap')
    def simulation_model_serializer(self, handler) -> Dict[str, Any]:

        serialized_dict = {}
        serialized_dict["name"] = self.name
        serialized_dict["num_events"] = self.num_events
        if self.momentum_min == self.momentum_max:
            serialized_dict["momentum"] = str(self.momentum_min)
        else:
            serialized_dict["momentum_min"] = str(self.momentum_min)
            serialized_dict["momentum_max"] = str(self.momentum_max)
        serialized_dict["enable_gun"] = self.enable_gun
        serialized_dict["particle"] = str(self.particle.value)
        serialized_dict["multiplicity"] = self.multiplicity
        serialized_dict["detector_relative_path"] = str(self.detector_relative_path)
        return serialized_dict


