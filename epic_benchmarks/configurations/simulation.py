from dataclasses import dataclass, fields, field, is_dataclass
from typing import Dict, Union

from epic_benchmarks.configurations._simulation._validation import validateMomentum, formatMomentum
from epic_benchmarks.configurations._simulation.executable import NpsimFlag, EicreconFlag, NpsimExecutable, EicreconExecutable
from epic_benchmarks.configurations._simulation.types import Particle, GunDistribution
from epic_benchmarks.configurations._config import BaseConfig, ConfigKey

NPSIM_METADATA_KEY = "npsim"
EICRECON_METADATA_KEY = "eicrecon"

@dataclass
class SimulationConfig(BaseConfig):
    name: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="name",
        types=str,
        default=None,
        optional=False,
    ))
    detector_build_path: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="detector_build_path",
        types=str,
        default="tracking/epic_craterlake_tracking_only.xml",
        optional=False,
        metadata={"npsim": NpsimFlag.CompactFile, "eicrecon": EicreconFlag.CompactFile}
    ))
    num_events: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="num_events",
        types=[str, int],
        default=1000,
        metadata={"npsim": NpsimFlag.NumEvents, "eicrecon": EicreconFlag.NumEvents}
    ))
    enable_gun: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="enable_gun",
        types=bool,
        default=True,
        metadata={NPSIM_METADATA_KEY : NpsimFlag.EnableGun}
    ))
    gun_distribution: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="gun_distribution",
        types=[GunDistribution, str],
        default=GunDistribution.Uniform,
        optional=False,
        validator=lambda g: g in GunDistribution,
        metadata={NPSIM_METADATA_KEY: NpsimFlag.GunDistribution}
    ))
    gun_particle: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="gun_particle",
        types=[Particle, str],
        default=Particle.PionNeutral,
        validator=lambda p: p in Particle,
        metadata={NPSIM_METADATA_KEY: NpsimFlag.GunParticle}
    ))
    multiplicity: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="multiplicity",
        types=[int, float, str],
        default=1,
        validator=lambda m: float(m) > 0,
        metadata={NPSIM_METADATA_KEY: NpsimFlag.GunMultiplicity}
    ))
    momentum_max: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="momentum_max",
        types=[int, float, str],
        default="10*GeV",
        optional=False,
        factory=formatMomentum,
        validator=validateMomentum,
        metadata={NPSIM_METADATA_KEY: NpsimFlag.GunMomentumMax}
    ))
    momentum_min: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="momentum_min",
        types=[int, float, str],
        default="10*GeV",
        optional=False,
        factory=formatMomentum,
        validator=validateMomentum,
        metadata={NPSIM_METADATA_KEY: NpsimFlag.GunMomentumMin}
    ))
    theta_max: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="theta_max",
        types=[int, float, str],
        default=None,
        optional=True,
        validator=lambda t: -90.0 <= float(t) <= 90.0,
        metadata={NPSIM_METADATA_KEY: NpsimFlag.GunThetaMax}
    ))
    theta_min: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="theta_min",
        types=[int, float, str],
        default=None,
        optional=True,
        validator=lambda t: -90.0 <= float(t) <= 90.0,
        metadata={NPSIM_METADATA_KEY: NpsimFlag.GunThetaMin}
    ))
    eta_max: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="eta_max",
        types=[int, float, str],
        default=None,
        optional=True,
        validator=lambda t: -100 <= float(t) <= 100,
        metadata={NPSIM_METADATA_KEY: NpsimFlag.GunEtaMax}
    ))
    eta_min: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="eta_min",
        types=[int, float, str],
        optional=True,
        default=None,
        validator=lambda t: -100 <= float(t) <= 100,
        metadata={NPSIM_METADATA_KEY : NpsimFlag.GunEtaMin}
    ))
    npsim_additional_flags: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="npsim_additional_flags",
        types=Dict[str, Union[int, float, str, None]],
        default=None,
    ))
    eicrecon_additional_flags: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="eicrecon_additional_flags",
        types=Dict[str, Union[int, float, str, None]],
        default=None,
    ))
    _npsim_exec : NpsimExecutable = field(default_factory=NpsimExecutable, init=False)
    _eicrecon_exec : EicreconExecutable = field(default_factory=EicreconExecutable, init=False)


    # def __init__(self, load_dict=None, load_filepath=None, **kwargs):
    #     super().__init__(load_dict=load_dict, load_filepath=load_filepath, kwargs=kwargs)

    def __post_init__(self):

        super().__post_init__()
        #Extra validation:

        #1) Either Eta or Theta must be specified. Not both.
        #2) Max values for Momentum, Eta, Theta must be bigger or equal to Min values for respective attribute
        #3)

        self._populate_npsim_exec()
        self._populate_eicrecon_exec()

    def npsimCommand(self, output_dir : str, output_file : str, compact_dir : str):

        #Validate that all relevant configurations have been made

        output_npsim = self._npsim_exec.OutputFile


    def eicreconCommand(self, input_dir : str, input_file : str, output_dir : str, output_file : str, compact_dir : str):

        # Validate that all relevant configurations have been made

        output_eicrecon = self._eicrecon_exec.OutputFile

    def _populate_npsim_exec(self):
        self._populate_exec(NPSIM_METADATA_KEY)

    def _populate_eicrecon_exec(self):
        self._populate_exec(EICRECON_METADATA_KEY)

    def _populate_exec(self, exec_key):
        try:
            for key in self.keys():
                key_metadata = self.key_metadata(key)
                if exec_key in key_metadata.keys():
                    key_flag = key_metadata[exec_key]
                    key_value = self.key_val(key)
                    if exec_key == NPSIM_METADATA_KEY:
                        self._npsim_exec.setFlagValue(key_flag, key_value)
                    elif exec_key == EICRECON_METADATA_KEY:
                        self._eicrecon_exec.setFlagValue(key_flag, key_value)
        except Exception as e:
            raise e

@dataclass
class CommonSimulationConfig(SimulationConfig):

    _is_common_config : bool = field(default=True, init=False)

def npsim_command(common_config : CommonSimulationConfig, instance_config : SimulationConfig):

    raise NotImplementedError

sim_test = SimulationConfig(
    name="Test",
    num_events=10000,
    gun_particle=Particle.PionNeutral,
    gun_distribution=GunDistribution.Eta,
    momentum_max="10GeV",
    momentum_min="10GeV",
    eta_max=4,
    eta_min=-4,
    detector_build_path="tracking/epic_craterlake_tracking_only.xml"
)




