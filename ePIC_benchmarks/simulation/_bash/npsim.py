from typing import Annotated, Optional, TypeVar, Literal, Generic, Union
from pydantic import Field, PlainSerializer

from ePIC_benchmarks._bash.flags import BashFlag, BashCommand
from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks.simulation.simulation_types import GunDistribution, Particle, Momentum, Angle, Eta


T = TypeVar('T')

class NpsimFlag(BashFlag[T], Generic[T]):
    pass

class NpsimCompactFileFlag(NpsimFlag[PathType]):
    flag : Literal["--compactFile"] = "--compactFile"

class NpsimNumEventsFlag(NpsimFlag[int]):
    flag : Literal["--numberOfEvents"] = "--numberOfEvents"

class EnableGunFlag(NpsimFlag[bool]):
    flag : Literal["--enableGun"] = "--enableGun"

class GunDistributionFlag(NpsimFlag[Union[str, GunDistribution]]):
    flag : Literal["--gun.distribution"] = "--gun.distribution"
    use_enum_val : bool = True

class GunParticleFlag(NpsimFlag[Union[str, Particle]]):
    flag : Literal["--gun.particle"] = "--gun.particle"
    use_enum_val : bool = True

class GunMomentumMaxFlag(NpsimFlag[Union[str, Momentum]]):
    flag : Literal["--gun.momentumMax"] = "--gun.momentumMax"

class GunMomentumMinFlag(NpsimFlag[Union[str, Momentum]]):
    flag : Literal["--gun.momentumMin"] = "--gun.momentumMin"

class GunThetaMaxFlag(NpsimFlag[Union[str, Angle]]):
    flag : Literal["--gun.thetaMax"] = "--gun.thetaMax"

class GunThetaMinFlag(NpsimFlag[Union[str, Angle]]):
    flag : Literal["--gun.thetaMin"] = "--gun.thetaMin"

class GunEtaMaxFlag(NpsimFlag[Union[str, Eta]]):
    flag : Literal["--gun.etaMax"] = "--gun.etaMax"

class GunEtaMinFlag(NpsimFlag[Union[str, Eta]]):
    flag : Literal["--gun.etaMin"] = "--gun.etaMin"

class GunMultiplicityFlag(NpsimFlag[float]):
    flag : Literal["--gun.multiplicity"] = "--gun.multiplicity"

class NpsimOutFileFlag(NpsimFlag[float]):
    flag : Literal["--outputFile"] = "--outputFile"

class NpsimModel(BashCommand):

    executable_command : Literal["npsim"] = "npsim"

    num_events : Annotated[int, PlainSerializer(
        NpsimNumEventsFlag.flag_string,
        return_type=str
    )]
    momentum_min : Annotated[Union[Momentum, str], PlainSerializer(
        GunMomentumMinFlag.flag_string,
        return_type=str
    )] = Field(alias='momentum')
    momentum_max : Annotated[Union[Momentum, str], PlainSerializer(
        GunMomentumMaxFlag.flag_string,
        return_type=str
    )] = Field(alias='momentum')
    distribution_type : Annotated[Union[GunDistribution, str], PlainSerializer(
        GunDistributionFlag.flag_string,
        return_type=str
    )]
    theta_min : Annotated[Optional[Union[Angle, str]], PlainSerializer(
        GunThetaMinFlag.flag_string,
        return_type=str
    )] = None
    theta_max : Annotated[Optional[Union[Angle, str]], PlainSerializer(
        GunThetaMaxFlag.flag_string,
        return_type=str
    )] = None
    eta_min : Annotated[Optional[Union[Eta, str]], PlainSerializer(
        GunEtaMinFlag.flag_string,
        return_type=str
    )] = None
    eta_max : Annotated[Optional[Union[Eta, str]], PlainSerializer(
        GunEtaMaxFlag.flag_string,
        return_type=str
    )] = None
    enable_gun : Annotated[bool, PlainSerializer(
        EnableGunFlag.flag_string,
        return_type=str
    )]
    particle : Annotated[Union[Particle, str], PlainSerializer(
        GunParticleFlag.flag_string,
        return_type=str
    )]
    multiplicity : Annotated[float, PlainSerializer(
        GunMultiplicityFlag.flag_string,
        return_type=str
    )]
    detector_path : Annotated[PathType, PlainSerializer(
        NpsimCompactFileFlag.flag_string,
        return_type=str
    )]
    output_path : Annotated[PathType, PlainSerializer(
        NpsimOutFileFlag.flag_string,
        return_type=str
    )]


