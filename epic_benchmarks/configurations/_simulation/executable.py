from dataclasses import dataclass, field, fields, Field
from typing import Any

from epic_benchmarks.configurations.executable import BashExecutable, BashExecFlag
from epic_benchmarks.configurations._simulation.types import EtaRange

@dataclass(frozen=True)
class NpsimFlag:

    CompactFile: BashExecFlag = BashExecFlag("--compactFile", str, value_is_file=True, file_exists=True)
    NumEvents: BashExecFlag = BashExecFlag("--numberOfEvents", [str, int], value_is_numeric=True)
    EnableGun: BashExecFlag = BashExecFlag("--enableGun", None)
    GunDistribution: BashExecFlag = BashExecFlag("--gun.distribution", str)
    GunParticle: BashExecFlag = BashExecFlag("--gun.particle", str)
    GunMomentumMax: BashExecFlag = BashExecFlag("--gun.momentumMax", str)
    GunMomentumMin: BashExecFlag = BashExecFlag("--gun.momentumMin", str)
    GunThetaMax: BashExecFlag = BashExecFlag("--gun.thetaMax", str)
    GunThetaMin: BashExecFlag = BashExecFlag("--gun.thetaMin", str)
    GunEtaMax: BashExecFlag = BashExecFlag("--gun.etaMax", [int, float, str], value_is_numeric=True,
                                           value_range=EtaRange())
    GunEtaMin: BashExecFlag = BashExecFlag("--gun.etaMin", [int, float, str], value_is_numeric=True,
                                           value_range=EtaRange())
    GunMultiplicity: BashExecFlag = BashExecFlag("--gun.multiplicity", [int, float, str], value_is_numeric=True)
    OutputFile: BashExecFlag = BashExecFlag("--OutputFile", str, value_is_file=True)

@dataclass(frozen=True)
class EicreconFlag:

    CompactFile: BashExecFlag = BashExecFlag("-Pdd4hep:xml_files", str, value_is_file=True, file_exists=True)
    NumEvents: BashExecFlag = BashExecFlag("-Pjana:nevents", [str, int], value_is_numeric=True)
    NumThreads: BashExecFlag = BashExecFlag("-Pnthreads", [str, int], value_is_numeric=True)
    OutputFile: BashExecFlag = BashExecFlag("-Ppodio:output_file", str, value_is_file=True)
    InputFile: BashExecFlag = BashExecFlag("", str, value_is_file=True)

@dataclass
class NpsimExecutable(BashExecutable):

    def __init__(self):
        self.executable = "npsim"
        self._flag_container = NpsimFlag()
        super().__init__()


@dataclass
class EicreconExecutable(BashExecutable):

    def __init__(self):
        self.executable = "eicrecon"
        self._flag_container = EicreconFlag()
        self.last_flag = EicreconFlag.InputFile
        super().__init__()

    