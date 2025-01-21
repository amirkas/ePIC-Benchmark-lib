from __future__ import annotations
from pathlib import Path
from typing import Union, Optional
from pydantic import BaseModel, computed_field, Field

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

    epic_directory : Optional[Path] = Field(default=None, description="Path to the Epic repository")
    simulation_out_directory : Optional[Path] = Field(default=None, description="Path to output directory for npsim generated root files")
    reconstructions_out_directory : Optional[Path] = Field(default=None, description="Path to the output directory for eicrecon generated root files")

    compact_file_relative_path : Optional[Path] = Field(default=None, description="Path of detector compact file relative to epic repository root")
    simulation_out_file_name : Optional[str] = Field(default=None, description="Name for npsim generated root file")
    reconstruction_out_file_name: Optional[str] = Field(default=None, description="Name for eicrecon generated root file")

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
        



