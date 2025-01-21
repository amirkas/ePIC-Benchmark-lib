from __future__ import annotations
from pathlib import Path
from typing import Union, Optional
from pydantic import BaseModel, computed_field

from epic_benchmarks.simulation.filepaths._fields import SimulationFileFields
from epic_benchmarks.simulation.flags import NPSIM_METADATA_KEY, EICRECON_METADATA_KEY, NpsimFlag, EicreconFlag
from epic_benchmarks._file.types import PathType

ROOT_FILE_SUFFIX = ".root"
NPSIM_OUTPUT_FILE_PREFIX = "npsim_"
EICRECON_OUTPUT_FILE_PREFIX = "eicrecon_"

def generate_file_name(simulation_name : str, prefix : str, suffix : str):

    return f"{prefix}{simulation_name}{suffix}"

DETECTOR_PATH_FLAG_MAP = {
    NPSIM_METADATA_KEY : NpsimFlag.CompactFile.value,
    EICRECON_METADATA_KEY : EicreconFlag.CompactFile.value
}

NPSIM_OUTPUT_FLAG_MAP = {
    NPSIM_METADATA_KEY: NpsimFlag.OutputFile.value
}

EICRECON_INPUT_FLAG_MAP = {
    EICRECON_METADATA_KEY : EicreconFlag.InputFile.value
}

EICRECON_OUTPUT_FLAG_MAP = {
    EICRECON_METADATA_KEY: EicreconFlag.OutputFile.value
}

class SimulationFilePaths(BaseModel):

    epic_directory : Optional[Path] = SimulationFileFields.EPIC_DIRECTORY_FIELD.value
    simulation_out_directory : Optional[Path] = SimulationFileFields.SIMULATION_OUT_DIRECTORY_FIELD.value
    reconstructions_out_directory : Optional[Path] = SimulationFileFields.RECONSTRUCTION_OUT_DIRECTORY_FIELD.value

    compact_file_relative_path : Optional[Path] = SimulationFileFields.COMPACT_RELATIVE_PATH_FIELD.value
    simulation_out_file_name : Optional[str] = SimulationFileFields.SIMULATION_OUT_FILENAME_FIELD.value
    reconstruction_out_file_name: Optional[str] = SimulationFileFields.RECONSTRUCTION_OUT_FILENAME_FIELD.value

    @computed_field(json_schema_extra=DETECTOR_PATH_FLAG_MAP)
    @property
    def detector_build_path(self) -> Optional[Path]:

        if self.epic_directory:
            return self.epic_directory.joinpath(self.compact_file_relative_path).resolve()
        else:
            return None
    
    @computed_field(json_schema_extra=NPSIM_OUTPUT_FLAG_MAP)
    @property
    def npsim_out_path(self) -> Optional[Path]:

        if self.simulation_out_directory:
            return self.simulation_out_directory.joinpath(self.simulation_out_file_name).resolve()
        else:
            return None
        
    @computed_field(json_schema_extra=EICRECON_INPUT_FLAG_MAP)
    @property
    def eicrecon_in_path(self) -> Optional[Path]:

        return self.npsim_out_path

    @computed_field(json_schema_extra=EICRECON_OUTPUT_FLAG_MAP)
    @property
    def eicrecon_out_path(self) -> Optional[Path]:

        if self.reconstructions_out_directory:
            return self.reconstructions_out_directory.joinpath(self.reconstruction_out_file_name).resolve()
        else:
            return None
        
    @classmethod
    def construct_file_paths_model(
        cls, simulation_name : str,
        detector_build_relative_path : PathType,
        epic_repository_path : Optional[PathType]=None,
        simulation_output_dir_path : Optional[PathType]=None,
        reconstruction_output_dir_path : Optional[PathType]=None
        ) -> SimulationFilePaths:

        npsim_out_filename = generate_file_name(
            simulation_name=simulation_name,
            prefix=NPSIM_OUTPUT_FILE_PREFIX,
            suffix=ROOT_FILE_SUFFIX
        )
        eicrecon_out_filename = generate_file_name(
            simulation_name=simulation_name,
            prefix=EICRECON_OUTPUT_FILE_PREFIX,
            suffix=ROOT_FILE_SUFFIX
        )
        return SimulationFilePaths(
            epic_directory=epic_repository_path,
            simulation_out_directory=simulation_output_dir_path,
            reconstructions_out_directory=reconstruction_output_dir_path,
            compact_file_relative_path=detector_build_relative_path,
            simulation_out_file_name=npsim_out_filename,
            reconstruction_out_file_name=eicrecon_out_filename
        )
        



