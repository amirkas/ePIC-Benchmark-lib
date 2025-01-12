from dataclasses import dataclass
from epic_benchmarks.configurations.executable import BashExecutable, BashExecFlag
from epic_benchmarks.configurations._validators import (
    is_file_path_readable, is_file_path_writeable, is_numeric, is_integer,
    is_particle, is_gun_distribution, is_momentum, is_angle, is_eta
)

# @dataclass(frozen=True)
# class NpsimFlag:
#
#     CompactFile: BashExecFlag = BashExecFlag("--compactFile", str, value_is_file=True) #TODO: Update file_exists behaviour
#     NumEvents: BashExecFlag = BashExecFlag("--numberOfEvents", [str, int], value_is_numeric=True)
#     EnableGun: BashExecFlag = BashExecFlag("--enableGun", [None, bool], include_bool=False)
#     GunDistribution: BashExecFlag = BashExecFlag("--gun.distribution", [str, GunDistribution])
#     GunParticle: BashExecFlag = BashExecFlag("--gun.particle", [str, Particle])
#     GunMomentumMax: BashExecFlag = BashExecFlag("--gun.momentumMax", [str, Quantity])
#     GunMomentumMin: BashExecFlag = BashExecFlag("--gun.momentumMin", [str, Quantity])
#     GunThetaMax: BashExecFlag = BashExecFlag("--gun.thetaMax", [str, Quantity])
#     GunThetaMin: BashExecFlag = BashExecFlag("--gun.thetaMin", [str, Quantity])
#     GunEtaMax: BashExecFlag = BashExecFlag("--gun.etaMax", [int, float, str, Quantity], value_is_numeric=True)
#     GunEtaMin: BashExecFlag = BashExecFlag("--gun.etaMin", [int, float, str, Quantity], value_is_numeric=True)
#     GunMultiplicity: BashExecFlag = BashExecFlag("--gun.multiplicity", [int, float, str], value_is_numeric=True)
#     OutputFile: BashExecFlag = BashExecFlag("--OutputFile", str, value_is_file=True)
#
# @dataclass(frozen=True)
# class EicreconFlag:
#
#     CompactFile: BashExecFlag = BashExecFlag("-Pdd4hep:xml_files", str, value_is_file=True) #TODO: Update file_exists behaviour
#     NumEvents: BashExecFlag = BashExecFlag("-Pjana:nevents", [str, int], value_is_numeric=True)
#     NumThreads: BashExecFlag = BashExecFlag("-Pnthreads", [str, int], value_is_numeric=True)
#     OutputFile: BashExecFlag = BashExecFlag("-Ppodio:output_file", str, value_is_file=True)
#     InputFile: BashExecFlag = BashExecFlag("", str, value_is_file=True)

@dataclass(frozen=True)
class NpsimFlag:
    CompactFile: BashExecFlag = BashExecFlag(
        flag="--compactFile",
        value_validators=is_file_path_readable
    )
    NumEvents: BashExecFlag = BashExecFlag(
        flag="--numberOfEvents", value_validators=is_integer,
        value_formatter=lambda x: int(x),
        enforce_value_as_string=False
    )
    EnableGun: BashExecFlag = BashExecFlag(
        flag="--enableGun",
        value_formatter=lambda x: ""
    )
    GunDistribution: BashExecFlag = BashExecFlag(
        flag="--gun.distribution",
        value_validators=is_gun_distribution,
        value_formatter=lambda x : str(x)
    )
    GunParticle: BashExecFlag = BashExecFlag(
        flag="--gun.particle",
        value_validators=is_particle,
        value_formatter=lambda x : str(x)
    )
    GunMomentumMax: BashExecFlag = BashExecFlag(
        flag="--gun.momentumMax",
        value_validators=is_momentum,
        value_formatter=lambda x : str(x)
    )
    GunMomentumMin: BashExecFlag = BashExecFlag(
        flag="--gun.momentumMin",
        value_validators=is_momentum,
        value_formatter=lambda x : str(x)
    )
    GunThetaMax: BashExecFlag = BashExecFlag(
        flag="--gun.thetaMax",
        value_validators=is_angle,
        value_formatter=lambda x : str(x)
    )
    GunThetaMin: BashExecFlag = BashExecFlag(
        flag="--gun.thetaMin",
        value_validators=is_angle,
        value_formatter=lambda x : str(x)
    )
    GunEtaMax: BashExecFlag = BashExecFlag(
        flag="--gun.etaMax",
        value_validators=is_eta,
        value_formatter=lambda x : str(x)
    )
    GunEtaMin: BashExecFlag = BashExecFlag(
        flag="--gun.etaMin",
        value_validators=is_eta,
        value_formatter=lambda x : str(x)
    )
    GunMultiplicity: BashExecFlag = BashExecFlag(
        flag="--gun.multiplicity",
        value_validators=is_numeric,
        value_formatter=lambda x : float(x)
    )
    OutputFile: BashExecFlag = BashExecFlag(
        flag="--OutputFile",
        value_validators=is_file_path_writeable
    )

@dataclass(frozen=True)
class EicreconFlag:
    CompactFile: BashExecFlag = BashExecFlag(
        flag="-Pdd4hep:xml_files",
        value_validators=is_file_path_readable
    )
    NumEvents: BashExecFlag = BashExecFlag(
        flag="-Pjana:nevents",
        value_validators=is_integer,
        value_formatter=lambda x: int(x),
        enforce_value_as_string=False
    )
    NumThreads: BashExecFlag = BashExecFlag(
        flag="-Pnthreads",
        value_validators=is_integer,
        value_formatter=lambda x: int(x),
        enforce_value_as_string=False
    )
    OutputFile: BashExecFlag = BashExecFlag(
        flag="-Ppodio:output_file",
        value_validators=is_file_path_writeable
    )
    InputFile: BashExecFlag = BashExecFlag(
        flag="",
        value_validators=is_file_path_writeable
    )

@dataclass
class NpsimExecutable(BashExecutable):

    def __init__(self):
        self.executable = "npsim"
        self._flag_container = NpsimFlag()
        self.required_flags = set([
            NpsimFlag.CompactFile, NpsimFlag.NumEvents, NpsimFlag.EnableGun,
            NpsimFlag.GunDistribution, NpsimFlag.GunParticle,
            NpsimFlag.GunMomentumMax, NpsimFlag.GunMomentumMin,
            set([NpsimFlag.GunThetaMax, NpsimFlag.GunEtaMax]),
            set([NpsimFlag.GunThetaMin, NpsimFlag.GunEtaMin]),
            NpsimFlag.GunMultiplicity, NpsimFlag.OutputFile
        ])
        super().__init__()


@dataclass
class EicreconExecutable(BashExecutable):

    def __init__(self):
        self.executable = "eicrecon"
        self._flag_container = EicreconFlag()
        self.required_flags = set([
            EicreconFlag.CompactFile, EicreconFlag.NumEvents,
            EicreconFlag.InputFile, EicreconFlag.OutputFile
        ])
        self.last_flag = EicreconFlag.InputFile
        super().__init__()

    