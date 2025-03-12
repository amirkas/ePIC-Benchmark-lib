from typing import Annotated, Optional, TypeVar, Literal, Generic
from pydantic import PlainSerializer

from ePIC_benchmarks._bash.flags import BashFlag, BashCommand
from ePIC_benchmarks._file.types import PathType

T = TypeVar('T')

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

class EicreconModel(BashCommand):

    executable_command : Literal["eicrecon"] = "eicrecon"

    detector_path : Annotated[PathType, PlainSerializer(
        EicreconCompactFileFlag.flag_string,
        return_type=str
    )]
    num_events : Annotated[int, PlainSerializer(
        EicreconNumEventsFlag.flag_string,
        return_type=str
    )]
    material_map_path : Annotated[Optional[PathType], PlainSerializer(
        MaterialMapFlag.flag_string,
        return_type=str
    )] = None
    output_path : Annotated[PathType, PlainSerializer(
        EicreconOutFileFlag.flag_string,
        return_type=str
    )]
    input_path : Annotated[PathType, PlainSerializer(
        EicreconInFileFlag.flag_string,
        return_type=str
    )]