from typing import Annotated, Optional, TypeVar, Literal, Generic
from pydantic import PlainSerializer

from ePIC_benchmarks._bash.flags import BashFlag, BashCommand
from ePIC_benchmarks._file.types import PathType


T = TypeVar('T')

###########################
### Eicrecon Bash Flags ###
###########################
class EicreconFlag(BashFlag[T], Generic[T]):
    pass

class EicreconCompactFileFlag(EicreconFlag[PathType]):
    flag : Literal["-Pdd4hep:xml_files"] = "-Pdd4hep:xml_files"

class EicreconNumEventsFlag(EicreconFlag[PathType]):
    flag : Literal["-Pjana:nevents"] = "-Pjana:nevents"

class EicreconNumThreadsFlag(EicreconFlag[int]):
    flag : Literal["-Pnthreads"] = "-Pnthreads"

class MaterialMapFlag(EicreconFlag[int]):
    flag : Literal["-Pacts:MaterialMap"] = "-Pacts:MaterialMap"

class EicreconOutFileFlag(EicreconFlag[PathType]):
    flag : Literal["-Ppodio:output_file"] = "-Ppodio:output_file"

class EicreconInFileFlag(EicreconFlag[PathType]):
    flag : Literal[""] = ""


################################################################################################
### NOTE: that attribute names must be identical to the attribute names in Simulation Config ###
################################################################################################

#Model that produces the full eicrecon command with required and optional flags
class EicreconModel(BashCommand):

    #The string format for the eicrecon bash executable
    executable_command : Literal["eicrecon"] = "eicrecon"

    #Required flag for specifying the detector build file to run reconstructions on
    detector_path : Annotated[PathType, PlainSerializer(
        EicreconCompactFileFlag.flag_string,
        return_type=str
    )]
    #Required flag for specifying the number of events to reconstruct
    num_events : Annotated[int, PlainSerializer(
        EicreconNumEventsFlag.flag_string,
        return_type=str
    )]
    #Optional flag for specifying the material map used on the detector build file
    material_map_path : Annotated[Optional[PathType], PlainSerializer(
        MaterialMapFlag.flag_string,
        return_type=str
    )] = None
    #Required flag for specifying the path of the eicrecon output root file 
    output_path : Annotated[PathType, PlainSerializer(
        EicreconOutFileFlag.flag_string,
        return_type=str
    )]
    #Required flag for specifying the path of the npsim output root file
    input_path : Annotated[PathType, PlainSerializer(
        EicreconInFileFlag.flag_string,
        return_type=str
    )]