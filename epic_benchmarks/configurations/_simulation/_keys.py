from dataclasses import dataclass, fields
from typing import Dict, List
from epic_benchmarks.configurations._config import ConfigKey, ConfigKeyContainer
from epic_benchmarks.configurations._simulation.types import GunDistribution, Particle
from epic_benchmarks.configurations._simulation._validation import formatMomentum, validateMomentum
from epic_benchmarks.configurations._simulation.flags import NpsimExecutable, EicreconExecutable

NPSIM_METADATA_KEY = "npsim"
EICRECON_METADATA_KEY = "eicrecon"

@dataclass
class SimulationKeyContainer(ConfigKeyContainer):

    name = ConfigKey(
        key_name="name",
        types=str,
        default=None
    )
    detector_build_path = ConfigKey(
        key_name="detector_build_path",
        types=str,
        default="tracking/epic_craterlake_tracking_only.yml",
        metadata={"npsim" : NpsimExecutable.CompactFile, "eicrecon" : EicreconExecutable.CompactFile}
    )
    num_events = ConfigKey(
        key_name="num_events",
        types=[str, int],
        default=1000,
        metadata={"npsim" : NpsimExecutable.NumEvents, "eicrecon" : EicreconExecutable.NumEvents}
    )
    enable_gun = ConfigKey(
        key_name="enable_gun",
        types=bool,
        default=True
    )
    gun_distribution = ConfigKey(
        key_name="gun_distribution",
        types=[GunDistribution, str],
        default=GunDistribution.Theta,
        validator=lambda g : g in GunDistribution,
        metadata={"npsim" : NpsimExecutable.GunDistribution}
    )
    gun_particle = ConfigKey(
        key_name="gun_particle",
        types=[Particle, str],
        default=Particle.PionNeutral,
        validator=lambda p: p in Particle,
        metadata={"npsim" : NpsimExecutable.GunParticle}
    )
    multiplicity = ConfigKey(
        key_name="multiplicity",
        types=[int, float, str],
        default=1,
        validator=lambda m : float(m) > 0,
        metadata={"npsim" : NpsimExecutable.GunMultiplicity}
    )
    momentum_max = ConfigKey(
        key_name="momentum_max",
        types=[int, float, str],
        default="10*GeV",
        factory=formatMomentum,
        validator=validateMomentum,
        metadata={"npsim" : NpsimExecutable.GunMomentumMax}
    )
    momentum_min = ConfigKey(
        key_name="momentum_min",
        types=[int, float, str],
        default="10*GeV",
        factory=formatMomentum,
        validator=validateMomentum,
        metadata={"npsim" : NpsimExecutable.GunMomentumMin}
    )
    theta_max = ConfigKey(
        key_name="theta_max",
        types=[int, float, str],
        default=None,
        validator=lambda t : float(t) >= -90.0 and float(t) <= 90.0,
        metadata={"npsim" : NpsimExecutable.GunThetaMax}
    )
    theta_min = ConfigKey(
        key_name="theta_min",
        types=[int, float, str],
        default=None,
        validator=lambda t : float(t) >= -90.0 and float(t) <= 90.0,
        metadata={"npsim" : NpsimExecutable.GunThetaMin}
    )
    eta_max = ConfigKey(
        key_name="eta_max",
        types=[int, float, str],
        default=None,
        validator=lambda t : float(t) >= -100 and float(t) <= 100,
        metadata={"npsim" : NpsimExecutable.GunEtaMax}
    )
    eta_min = ConfigKey(
        key_name="eta_min",
        types=[int, float, str],
        default=None,
        validator=lambda t : float(t) >= -100 and float(t) <= 100,
        metadata={"npsim" : NpsimExecutable.GunEtaMin}
    )
    npsim_additional_flags = ConfigKey(
        key_name="npsim_additional_flags",
        types=Dict[str, int | float | str | None],
        default="{}",
    )
    eicrecon_additional_flags = ConfigKey(
        key_name="eicrecon_additional_flags",
        types=Dict[str, int | float | str | None],
        default="{}",
    )

