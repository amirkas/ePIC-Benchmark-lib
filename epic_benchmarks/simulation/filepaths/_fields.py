from enum import Enum
from pydantic import Field

class SimulationFileFields(Enum):

    EPIC_DIRECTORY_FIELD = Field(default=None, description="Path to the Epic repository")
    SIMULATION_OUT_DIRECTORY_FIELD = Field(default=None, description="Path to output directory for npsim generated root files")
    RECONSTRUCTION_OUT_DIRECTORY_FIELD = Field(default=None, description="Path to the output directory for eicrecon generated root files")
    
    COMPACT_RELATIVE_PATH_FIELD = Field(default=None, description="Path of detector compact file relative to epic repository root")
    SIMULATION_OUT_FILENAME_FIELD = Field(default=None, description="Name for npsim generated root file")
    RECONSTRUCTION_OUT_FILENAME_FIELD = Field(default=None, description="Name for eicrecon generated root file")

