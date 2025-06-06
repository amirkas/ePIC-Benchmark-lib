from typing import Annotated, Optional, TypeVar, Literal, Generic, Union
from pydantic import Field, PlainSerializer

from ePIC_benchmarks._bash.flags import BashFlag, BashCommand
from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks.simulation.simulation_types import GunDistribution, Particle, Momentum, Angle, Eta


T = TypeVar('T')

########################
### Npsim Bash Flags ###
########################
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

################################################################################################
### NOTE: that attribute names must be identical to the attribute names in Simulation Config ###
################################################################################################

class NpsimModel(BashCommand):

    #The string format for the npsim bash executable
    executable_command : Literal["npsim"] = "npsim"

    #Required flag that specifies the number of particle events to simulate
    num_events : Annotated[int, PlainSerializer(
        NpsimNumEventsFlag.flag_string,
        return_type=str
    )]

    #Required flag that specifies the minimum momentum for simulated particles
    momentum_min : Annotated[Union[Momentum, str], PlainSerializer(
        GunMomentumMinFlag.flag_string,
        return_type=str
    )] = Field(alias='momentum')

    #Required flag that specifies the maximum momentum for simulated particles
    momentum_max : Annotated[Union[Momentum, str], PlainSerializer(
        GunMomentumMaxFlag.flag_string,
        return_type=str
    )] = Field(alias='momentum')

    #Required flag that specifies the phase space of the simulation
    distribution_type : Annotated[Union[GunDistribution, str], PlainSerializer(
        GunDistributionFlag.flag_string,
        return_type=str
    )]

    #Optional flag that specifies the minimum angle in degrees for particle events
    #NOTE: Must use 'Uniform' phase space
    theta_min : Annotated[Optional[Union[Angle, str]], PlainSerializer(
        GunThetaMinFlag.flag_string,
        return_type=str
    )] = None

    #Optional flag that specifies the maximum angle in degrees for particle events
    #NOTE: Must use 'Uniform' phase space
    theta_max : Annotated[Optional[Union[Angle, str]], PlainSerializer(
        GunThetaMaxFlag.flag_string,
        return_type=str
    )] = None

    #Optional flag that specifies the minimum pseudorapidity for particle events
    #NOTE: Must use 'Eta' phase space
    eta_min : Annotated[Optional[Union[Eta, str]], PlainSerializer(
        GunEtaMinFlag.flag_string,
        return_type=str
    )] = None

    #Optional flag that specifies the maximum pseudorapidity for particle events
    #NOTE: Must use 'Eta' phase space
    eta_max : Annotated[Optional[Union[Eta, str]], PlainSerializer(
        GunEtaMaxFlag.flag_string,
        return_type=str
    )] = None

    #Required flag that specifies whether the particle gun is enabled
    enable_gun : Annotated[bool, PlainSerializer(
        EnableGunFlag.flag_string,
        return_type=str
    )]

    #Required flag that specifies the particle to simulate
    particle : Annotated[Union[Particle, str], PlainSerializer(
        GunParticleFlag.flag_string,
        return_type=str
    )]

    #Required flag that specifies the multiplicity of particle events
    multiplicity : Annotated[float, PlainSerializer(
        GunMultiplicityFlag.flag_string,
        return_type=str
    )]

    #Required flag that specifies the detector build path to run simulations on
    detector_path : Annotated[PathType, PlainSerializer(
        NpsimCompactFileFlag.flag_string,
        return_type=str
    )]

    #Required flag that specifies the output path for the npsim executable
    output_path : Annotated[PathType, PlainSerializer(
        NpsimOutFileFlag.flag_string,
        return_type=str
    )]


