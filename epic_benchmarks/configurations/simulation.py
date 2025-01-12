import numbers
import os
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field, model_validator, \
    field_validator, field_serializer, AliasChoices, AliasPath, computed_field, ConfigDict, PrivateAttr
from typing import Dict, Union, Optional, Annotated, Tuple, Any, List, Self, Callable

from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, CliPositionalArg, CliImplicitFlag, CliExplicitFlag, \
    CliMutuallyExclusiveGroup
from typing_extensions import TypeVar

from epic_benchmarks.configurations._config import ConfigurationModel
from epic_benchmarks.configurations._simulation.executable import NpsimFlag, EicreconFlag, NpsimExecutable, EicreconExecutable
from epic_benchmarks.configurations.simulation_types import Particle, GunDistribution, Quantity, Momentum, Angle, Eta
from epic_benchmarks.configurations.executable import BashExecutable, BashExecFlag

NPSIM_METADATA_KEY = "npsim"
EICRECON_METADATA_KEY = "eicrecon"

DistributionTypes = Union[Angle, Eta]



class SimulationConfig(ConfigurationModel):


    detector_path : str = Field(description="Relative path to the detector description in the epic repository")
    num_events : int = Field(
        json_schema_extra={
            NPSIM_METADATA_KEY : NpsimFlag.NumEvents,
            EICRECON_METADATA_KEY : EicreconFlag.NumEvents,
        },
        description="Number of events to simulate",
    )
    momentum_min : Momentum = Field(
        validation_alias=AliasChoices(
            'momentum_min',
            'min_momentum',
            'momentum',
            AliasPath('momentum_range', 0),
            AliasPath('momenta', 0)
        ),
        json_schema_extra={ NPSIM_METADATA_KEY : NpsimFlag.GunMomentumMin },
        description="Minimum momentum value (or static momentum value)",
    )
    momentum_max: Momentum = Field(
        validation_alias=AliasChoices(
            'momentum_max',
            'max_momentum',
            'momentum',
            AliasPath('momentum_range', 0),
            AliasPath('momenta', 0)
        ),
        json_schema_extra={NPSIM_METADATA_KEY: NpsimFlag.GunMomentumMax},
        description="Maximum momentum value (or static momentum value)",
    )
    distribution: GunDistribution = Field(
        default=GunDistribution.Uniform,
        validate_default=True,
        json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.GunDistribution}
    )
    distribution_min : Optional[DistributionTypes] = Field(
        validation_alias=AliasChoices(
            'distribution_min',
            'dist_min',
            'angle_min',
            'min_angle',
            AliasPath('distribution_range', 0),
            AliasPath('dist_range', 0),
        ),
        json_schema_extra={
            GunDistribution.Uniform.value: {NPSIM_METADATA_KEY: NpsimFlag.GunThetaMax},
            GunDistribution.Eta.value: {NPSIM_METADATA_KEY: NpsimFlag.GunEtaMax}
        }
    )
    distribution_max : Optional[DistributionTypes] = Field(
        validation_alias=AliasChoices(
            'distribution_max',
            'dist_max',
            'angle_max',
            'max_angle',
            AliasPath('distribution_range', 1),
            AliasPath('dist_range', 1),
        ),
    )
    enable_gun : bool = Field(
        default=True,
        validate_default=True,
        json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.EnableGun}
    )
    particle : Particle = Field(
        default=Particle.PionNeutral,
        validate_default=True,
        json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.GunParticle}
    )
    multiplicity : float = Field(
        default=1.0,
        validate_default=True,
        json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.GunMultiplicity}
    )
    name: Optional[str] = Field(default=None, description="Name of the simulation")

    theta_min : Optional[Angle] = Field(
        default=None,
        validation_alias=AliasChoices(
            'theta_min',
            'min_theta',
            AliasPath('theta_range', 0),
        ),
        json_schema_extra={
            NPSIM_METADATA_KEY : NpsimFlag.GunThetaMin
        },
        exclude=True,
        init=False
    )
    theta_max : Optional[Angle] = Field(
        default=None,
        validation_alias=AliasChoices(
            'theta_max',
            'max_theta',
            AliasPath('theta_range', 1),
        ),
        json_schema_extra={
            NPSIM_METADATA_KEY: NpsimFlag.GunThetaMax
        },
        exclude=True,
        init=False
    )
    eta_min : Optional[Eta] = Field(
        default=None,
        validation_alias=AliasChoices(
            'eta_min',
            'min_eta',
            AliasPath('eta_range', 0),
        ),
        json_schema_extra={
            NPSIM_METADATA_KEY: NpsimFlag.GunEtaMin
        },
        exclude=True,
        init=False
    )
    eta_max : Optional[Eta] = Field(
        default=None,
        validation_alias=AliasChoices(
            'eta_max',
            'max_eta',
            AliasPath('eta_range', 1),
        ),
        json_schema_extra={
            NPSIM_METADATA_KEY: NpsimFlag.GunEtaMax
        },
        exclude=True,
        init=False
    )
    npsim_output_file_path : Optional[Union[Path, str]] = Field(
        default=None,
        json_schema_extra={
            NPSIM_METADATA_KEY: NpsimFlag.OutputFile,
        },
        exclude=True
    )
    eicrecon_input_file_path : Optional[Union[Path, str]] = Field(
        default=None,
        json_schema_extra={
            EICRECON_METADATA_KEY : EicreconFlag.InputFile,
        },
        exclude=True
    )
    eicrecon_output_file_path : Optional[Union[Path, str]] = Field(
        default=None,
        json_schema_extra={
            EICRECON_METADATA_KEY: EicreconFlag.OutputFile,
        },
        exclude=True
    )
    full_detector_filepath : Optional[Union[Path, str]] = Field(
        default=None,
        json_schema_extra={
            NPSIM_METADATA_KEY : NpsimFlag.CompactFile,
            EICRECON_METADATA_KEY : EicreconFlag.CompactFile
        },
        exclude=True,
        init=False
    )
    def npsim_cmd(self, epic_repo_path : Optional[Union[Path, str]]=None, output_dir_path : Optional[Union[Path, str]]=None):
        detector_path = Path(self.detector_path).resolve()
        if epic_repo_path:
            epic_repo_path = Path(epic_repo_path).resolve()
            detector_path = epic_repo_path.joinpath(detector_path)
        output_path = Path(self.npsim_filename).resolve()
        if output_dir_path:
            output_dir_path = Path(output_dir_path).resolve()
            output_path = output_dir_path.joinpath(output_path)
        self.full_detector_filepath = detector_path
        self.npsim_output_file_path = output_path
        self.eicrecon_input_file_path = output_path

        flag_str = self._generate_flag_str(NPSIM_METADATA_KEY)
        total_cmd = "npsim" + flag_str
        return total_cmd

        # npsim_exec = self._npsim_exec()
        # return npsim_exec.generate_cmd()

    def eicrecon_cmd(self, epic_repo_path : Optional[Union[Path, str]]=None, input_dir_path : Optional[Union[Path, str]]=None, output_dir_path : Optional[Union[Path, str]]=None):

        detector_path = Path(self.detector_path).resolve()
        if epic_repo_path:
            epic_repo_path = Path(epic_repo_path).resolve()
            detector_path = epic_repo_path.joinpath(detector_path)

        input_path = Path(self.eicrecon_input_file_path).resolve()
        if input_dir_path:
            input_dir_path = Path(input_dir_path).resolve()
            input_path = input_dir_path.joinpath(input_path)

        output_path = Path(self.eicrecon_output_file_path).resolve()
        if output_dir_path:
            output_dir_path = Path(output_dir_path).resolve()
            output_path = output_dir_path.joinpath(output_path)

        self.eicrecon_output_file_path = output_path
        self.eicrecon_input_file_path = input_path
        self.full_detector_filepath = detector_path

        flag_str = self._generate_flag_str(EICRECON_METADATA_KEY)
        total_cmd = "eicrecon" + flag_str
        return total_cmd

        #
        # eicrecon_exec = self._eicrecon_exec()
        # return eicrecon_exec.generate_cmd()

    @field_validator('name', mode='after')
    def validate_name(cls, value : Any, info : ValidationInfo) -> str:
        if value is None:

            _momentum_min = info.data["momentum_min"]
            _momentum_max = info.data["momentum_max"]
            _distribution_min = info.data["distribution_min"]
            _distribution_max = info.data["distribution_max"]

            if _momentum_min == _momentum_max:
                momentum_str = f"[{_momentum_min}]"
            else:
                momentum_str = f"[{_momentum_min}-{_momentum_max}]"
            distribution_str = f"{type(_distribution_min).__name__}[{_distribution_min}-{_distribution_max}]"
            return f"{distribution_str}_{momentum_str}"
        else:
            return value


    @field_validator('momentum_min', 'momentum_max', mode='before')
    def validate_momentum_limit(cls, value : Any) -> Momentum:
        return Momentum.to_quantity(value)


    #Validate and format the distribution limits if not None.
    @field_validator('distribution_min', 'distribution_max', mode='before')
    def pre_validate_distribution_limit(cls, value : Any, info : ValidationInfo) -> Union[Angle, Eta]:
        if value:
            context_distribution = info.data['distribution']
            if context_distribution == GunDistribution.Uniform.value:
                return Angle.to_quantity(value)
            elif context_distribution == GunDistribution.Eta.value:
                return Eta.to_quantity(value)
            else:
                err = f"Distribution '{context_distribution}' is not supported"
                raise NotImplementedError(err)
        return value

    #Set theta min to distribution min if distribution is uniform and distribution min is not None
    @field_validator('theta_min', mode='before')
    def set_theta_min(cls, value : Optional[DistributionTypes], info : ValidationInfo) -> Optional[Angle]:
        distribution_min = info.data['distribution_min']
        if distribution_min:
            return SimulationConfig._format_distribution_limit(distribution_min, Angle)
        elif value and isinstance(value, Angle) or value is None:
            return value
        else:
            return Angle(value)

    # Set theta max to distribution max if distribution is uniform and distribution max is not None
    @field_validator('theta_max', mode='before')
    def set_theta_max(cls, value : Optional[DistributionTypes], info : ValidationInfo) -> Optional[Angle]:
        distribution_max = info.data['distribution_max']
        if distribution_max:
            return SimulationConfig._format_distribution_limit(distribution_max, Angle)
        elif value and isinstance(value, Angle) or value is None:
            return value
        else:
            return Angle(value)

    # Set eta min to distribution min if distribution is uniform and distribution min is not None
    @field_validator('eta_min', mode='before')
    def set_eta_min(cls, value : Optional[DistributionTypes], info : ValidationInfo) -> Optional[Eta]:
        distribution_min = info.data['distribution_min']
        if distribution_min:
            return SimulationConfig._format_distribution_limit(distribution_min, Eta)
        elif value and isinstance(value, Eta) or value is None:
            return value
        else:
            return Eta(value)

    # Set eta max to distribution max if distribution is uniform and distribution max is not None
    @field_validator('eta_max', mode='before')
    def set_eta_max(cls, value : Optional[DistributionTypes], info : ValidationInfo) -> Optional[Eta]:
        distribution_max = info.data['distribution_max']
        if distribution_max:
            return SimulationConfig._format_distribution_limit(distribution_max, Eta)
        elif value and isinstance(value, Eta) or value is None:
            return value
        else:
            return Eta(value)

    # Ensure distribution min is set if either theta min or eta min is provided.
    # Primarily used for loading a model from a file
    @field_validator('distribution_min', mode='after')
    def post_validate_min_distribution(cls, value : Optional[DistributionTypes], info : ValidationInfo) -> DistributionTypes:
        if value is None:
            theta_min = info.data['theta_min']
            eta_min = info.data['eta_min']
            if theta_min:
                return theta_min
            else:
                return eta_min
        else:
            return value

    # Ensure distribution max is set if either theta max or eta max is provided.
    # Primarily used for loading a model from a file
    @field_validator('distribution_max', mode='after')
    def post_validate_max_distribution(cls, value: Optional[DistributionTypes], info: ValidationInfo) -> DistributionTypes:
        if value is None:
            theta_max = info.data['theta_max']
            eta_max = info.data['eta_max']
            if theta_max:
                return theta_max
            else:
                return eta_max
        else:
            return value




    # @field_validator('distribution_min', mode='before')
    # def validate_distribution_lower_limit(cls, value: Any, info: ValidationInfo) -> Union[Angle, Eta]:
    #     context_distribution = info.data['distribution']
    #     distribution_lower_limit = cls._format_distribution_limit(value, context_distribution)
    #     if isinstance(distribution_lower_limit, Angle):
    #         self.theta_min = distribution_lower_limit


    # @classmethod
    # def _format_distribution_limit(cls, value : Any, distribution : str) -> Union[Angle, Eta]:
    #
    #     if distribution == GunDistribution.Uniform.value:
    #         return Angle.to_quantity(value)
    #     elif distribution == GunDistribution.Eta.value:
    #         return Eta.to_quantity(value)
    #     else:
    #         err = f"Distribution '{distribution}' is not supported"
    #         raise NotImplementedError(err)

    # @model_validator(mode='after')
    # def set_private_distribution_limits(self) -> Self:
    #     if isinstance(self.distribution_min, Angle) and isinstance(self.distribution_max, Angle):
    #         self.theta_min = self.distribution_min
    #         self.theta_max = self.distribution_max
    #     elif isinstance(self.distribution_min, Eta) and isinstance(self.distribution_max, Eta):
    #         self.eta_min = self.distribution_min
    #         self.eta_max = self.distribution_max
    #     else:
    #         raise AttributeError("Both limits of a distribution must have the same type")
    #     return self

    @model_validator(mode='after')
    def validate_momentum_range(self) -> Self:

        if self.momentum_min < 0:
            raise ValueError("Minimum momentum must be non-negative")
        if self.momentum_max < 0:
            raise ValueError("Maximum momentum must be non-negative")
        if self.momentum_min > self.momentum_max:
            raise ValueError("Minimum momentum must be lower than or equal to the maximum momentum")
        return self

    @model_validator(mode='after')
    def validate_distribution_range(self) -> Self:
        if type(self.distribution_min) is not type(self.distribution_max):
            raise ValueError("Distribution range limits must be the same type")
        if self.distribution_min >= self.distribution_max:
            raise ValueError("Minimum distribution limit must be strictly lower than the maximum distribution limit")
        return self

    @field_serializer(
        'momentum_min', 'momentum_max',
        'distribution_min', 'distribution_max',
        'theta_min', 'theta_max', 'eta_min', 'eta_max',
    )
    def serialize_quantities(self, v : Any, _info) -> str:
        return str(v)

    #TODO: Exclude computed fields once Pydantic offers support for it.
    # @computed_field(json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.GunThetaMin}, repr=False)
    # @cached_property
    # def theta_min(self) -> Union[Angle, None]:
    #     if isinstance(self.distribution_min, Angle):
    #         return self.distribution_min
    #     return None
    #
    # @computed_field(json_schema_extra={NPSIM_METADATA_KEY: NpsimFlag.GunThetaMax}, repr=False)
    # @cached_property
    # def theta_max(self) -> Union[Angle, None]:
    #     if isinstance(self.distribution_max, Angle):
    #         return self.distribution_min
    #     return None
    #
    # @computed_field(json_schema_extra={NPSIM_METADATA_KEY: NpsimFlag.GunEtaMin}, repr=False)
    # @cached_property
    # def eta_min(self) -> Union[Angle, None]:
    #     if isinstance(self.distribution_min, Eta):
    #         return self.distribution_min
    #     return None
    #
    # @computed_field(json_schema_extra={NPSIM_METADATA_KEY: NpsimFlag.GunEtaMax}, repr=False)
    # @cached_property
    # def eta_max(self) -> Union[Angle, None]:
    #     if isinstance(self.distribution_max, Eta):
    #         return self.distribution_min
    #     return None

    @computed_field(json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.OutputFile, EICRECON_METADATA_KEY : EicreconFlag.InputFile})
    @cached_property
    def npsim_filename(self) -> str:
        return self._filename("sim")

    @computed_field(json_schema_extra={EICRECON_METADATA_KEY : EicreconFlag.OutputFile})
    @cached_property
    def eicrecon_filename(self) -> str:
        return self._filename("recon")

    def _generate_flag_str(self, executable_key : str) -> str:

        flag_str = ""
        for field_name, field_info in self.model_fields.items():
            if executable_key in field_info.json_schema_extra.keys():
                field_flag = field_info.json_schema_extra[executable_key]
                assert isinstance(field_flag, BashExecFlag)
                field_val = getattr(self, field_name, None)
                formatted_flag = field_flag.bash_format(field_val)
                flag_str += f" {formatted_flag}"
        return flag_str

    @classmethod
    def _format_distribution_limit(cls, distribution_value : Any, limit_type : TypeVar):
        if isinstance(distribution_value, limit_type):
            return distribution_value
        else:
            return None






    def _npsim_exec(self) -> NpsimExecutable:
        npsim_exec = NpsimExecutable()
        self._populate_executable(npsim_exec, NPSIM_METADATA_KEY)
        return npsim_exec

    def _eicrecon_exec(self) -> EicreconExecutable:
        eicrecon_exec = EicreconExecutable()
        self._populate_executable(eicrecon_exec, EICRECON_METADATA_KEY)
        return eicrecon_exec

    def _filename(self, prefix : str) -> str:

        return f"{prefix}_{self.name}.root"

    def _populate_executable(self, executable : BashExecutable, executable_key):

        all_fields_set = self.model_fields_set
        for attr_name, attr_data in all_fields_set.items():
            attr_metadata = attr_data.json_schema_extra
            if attr_metadata and executable_key in attr_metadata.keys():
                attr_flag = attr_metadata[executable_key]
                attr_value = getattr(self, attr_name, None)
                executable.set_flag_val(attr_flag, attr_value)
        return



class NpsimGun(BaseSettings):

    distribution : str
    particle : str
    thetaMin : str

class NpsimCLI(BaseSettings, cli_parse_args=True, cli_prog_name='npsim'):

    NumEvents : int
    gun : NpsimGun


gun_settings = NpsimGun(distribution="eta", particle="pi", thetaMin="10*degrees")
cli_settings = NpsimCLI(NumEvents=10, gun=gun_settings)

# print(cli_settings)



#
#
# @dataclass
# class SimulationConfig(BaseConfig):
#     name: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="name",
#         types=str,
#         default=None,
#         optional=False,
#     ))
#     detector_build_path: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="detector_build_path",
#         types=str,
#         default="tracking/epic_craterlake_tracking_only.xml",
#         optional=False,
#         metadata={"npsim": NpsimFlag.CompactFile, "eicrecon": EicreconFlag.CompactFile}
#     ))
#     num_events: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="num_events",
#         types=[str, int],
#         default=1000,
#         metadata={"npsim": NpsimFlag.NumEvents, "eicrecon": EicreconFlag.NumEvents}
#     ))
#     enable_gun: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="enable_gun",
#         types=bool,
#         default=True,
#         metadata={NPSIM_METADATA_KEY : NpsimFlag.EnableGun}
#     ))
#     gun_distribution: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="gun_distribution",
#         types=[GunDistribution, str],
#         default=GunDistribution.Uniform,
#         optional=False,
#         validator=lambda g: g in GunDistribution,
#         metadata={NPSIM_METADATA_KEY: NpsimFlag.GunDistribution}
#     ))
#     gun_particle: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="gun_particle",
#         types=[Particle, str],
#         default=Particle.PionNeutral,
#         validator=lambda p: p in Particle,
#         metadata={NPSIM_METADATA_KEY: NpsimFlag.GunParticle}
#     ))
#     multiplicity: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="multiplicity",
#         types=[int, float, str],
#         default=1,
#         validator=lambda m: float(m) > 0,
#         metadata={NPSIM_METADATA_KEY: NpsimFlag.GunMultiplicity}
#     ))
#     momentum_max: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="momentum_max",
#         types=[int, float, str],
#         default="10*GeV",
#         optional=False,
#         formatter=format_momentum,
#         validator=validate_momentum,
#         metadata={NPSIM_METADATA_KEY: NpsimFlag.GunMomentumMax}
#     ))
#     momentum_min: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="momentum_min",
#         types=[int, float, str],
#         default="10*GeV",
#         optional=False,
#         formatter=format_momentum,
#         validator=validate_momentum,
#         metadata={NPSIM_METADATA_KEY: NpsimFlag.GunMomentumMin}
#     ))
#     theta_max: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="theta_max",
#         types=[int, float, str],
#         default=None,
#         optional=True,
#         validator=lambda t: -90.0 <= float(t) <= 90.0,
#         metadata={NPSIM_METADATA_KEY: NpsimFlag.GunThetaMax}
#     ))
#     theta_min: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="theta_min",
#         types=[int, float, str],
#         default=None,
#         optional=True,
#         validator=lambda t: -90.0 <= float(t) <= 90.0,
#         metadata={NPSIM_METADATA_KEY: NpsimFlag.GunThetaMin}
#     ))
#     eta_max: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="eta_max",
#         types=[int, float, str],
#         default=None,
#         optional=True,
#         validator=lambda t: -100 <= float(t) <= 100,
#         metadata={NPSIM_METADATA_KEY: NpsimFlag.GunEtaMax}
#     ))
#     eta_min: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="eta_min",
#         types=[int, float, str],
#         optional=True,
#         default=None,
#         validator=lambda t: -100 <= float(t) <= 100,
#         metadata={NPSIM_METADATA_KEY : NpsimFlag.GunEtaMin}
#     ))
#     npsim_additional_flags: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="npsim_additional_flags",
#         types=Dict[str, Union[int, float, str, None]],
#         default=None,
#     ))
#     eicrecon_additional_flags: ConfigKey = field(default_factory=lambda: ConfigKey(
#         key_name="eicrecon_additional_flags",
#         types=Dict[str, Union[int, float, str, None]],
#         default=None,
#     ))
#     _npsim_exec : NpsimExecutable = field(default_factory=NpsimExecutable, init=False)
#     _eicrecon_exec : EicreconExecutable = field(default_factory=EicreconExecutable, init=False)
#
#     #TODO: Refactor function components into separate functions
#     # noinspection DuplicatedCode
#     def __post_init__(self):
#
#         super().__post_init__()
#         #If momentum_max is set, but not momentum_min, set momentum_min and vice versa.
#         if self.momentum_max and not self.momentum_min:
#             self.momentum_min = self.momentum_max
#         elif self.momentum_min and not self.momentum_max:
#             self.momentum_max = self.momentum_min
#
#         #Extra validation:
#         #1) Either Eta or Theta must be specified. Not both.
#         if (self.eta_max or self.eta_min) and (self.theta_max or self.theta_min):
#             raise ValueError("Cannot specify both theta ranges and eta ranges.")
#
#         #2) If One eta bound is specified, the other bound must be specified
#         if (self.eta_max and not self.eta_min) or (self.eta_min and not self.eta_max):
#             received_bound = "Lower Bound" if self.eta_min else "Upper Bound"
#             err = f"Must specify both the lower bound and the upper bound for Eta. Only received the {received_bound}"
#             raise ValueError(err)
#
#         #3) Same as #2 but for theta
#         if (self.theta_max and not self.theta_min) or (self.theta_min and not self.theta_max):
#             received_bound = "Lower Bound" if self.theta_min else "Upper Bound"
#             err = f"Must specify both the lower bound and the upper bound for Theta. Only received the {received_bound}"
#             raise ValueError(err)
#
#         #3) Max values for Eta or Theta must be bigger than Min values for respective attribute
#         if self.eta_max and ((self.eta_max <= self.eta_min) or (self.eta_min >= self.eta_max)):
#             if self.eta_max < self.eta_min:
#                 err = f"Eta Upper bound '{self.eta_max}' must be larger than Eta Lower bound '{self.eta_min}'"
#             else:
#                 err = f"Eta Lower bound '{self.eta_min}' must be smaller than Eta Upper bound '{self.eta_max}'"
#             raise ValueError(err)
#
#         if self.theta_max and ((self.theta_max <= self.theta_min) or (self.theta_min >= self.theta_max)):
#             if self.theta_max < self.theta_min:
#                 err = f"Theta Upper bound '{self.theta_max}' must be larger than Theta Lower bound '{self.theta_min}'"
#             else:
#                 err = f"Theta Lower bound '{self.theta_min}' must be smaller than Theta Upper bound '{self.theta_max}'"
#             raise ValueError(err)
#
#         #TODO: Ensure momentum comparison is correct given string formatting
#         #4) Similar to #2 but Momentum max can be bigger or equal to Momentum Min
#         if self.momentum_max and ((self.momentum_max < self.momentum_min) or (self.theta_min > self.momentum_min)):
#             if self.theta_max < self.momentum_min:
#                 err = f"Momentum Upper bound '{self.momentum_max}' must be larger than Momentum Lower bound '{self.momentum_min}'"
#             else:
#                 err = f"Momentum Lower bound '{self.momentum_min}' must be smaller than Momentum Upper bound '{self.momentum_max}'"
#             raise ValueError(err)
#
#         #5) TODO: Add validation for following
#         #6) Ensure build file exists by inspecting Repo for the desired branch.
#         self._populate_npsim_exec()
#         self._populate_eicrecon_exec()
#
#     def npsim_cmd(self, output_dir : str, compact_dir : str, output_file_name : Optional[str] = None):
#
#         output_npsim_flag = NpsimFlag.OutputFile
#         compact_npsim_flag = NpsimFlag.CompactFile
#
#         if not output_file_name:
#             output_file_name = self.npsim_filename()
#         output_file_path = os.path.join(output_dir, output_file_name)
#         detector_build_path = os.path.join(compact_dir, self.detector_build_path)
#
#         #Set flags for output file and detector build file
#         self._npsim_exec.set_flag_val(output_npsim_flag, output_file_path)
#         self._npsim_exec.set_flag_val(compact_npsim_flag, detector_build_path)
#         return self._npsim_exec.generate_cmd()
#
#
#     def eicrecon_cmd(self, input_dir : str, output_dir : str, compact_dir : str, input_file_name : Optional[str] = None, output_file_name : Optional[str] = None):
#
#         output_eicrecon_flag = EicreconFlag.OutputFile
#         compact_eicrecon_flag = EicreconFlag.CompactFile
#         input_eicrecon_flag = EicreconFlag.InputFile
#
#         if not output_file_name:
#             output_file_name = self.eicrecon_filename()
#         if not input_file_name:
#             input_file_name = self.npsim_filename()
#         output_file_path = os.path.join(output_dir, output_file_name)
#         input_file_path = os.path.join(input_dir, input_file_name)
#         detector_build_path = os.path.join(compact_dir, self.detector_build_path)
#
#         self._eicrecon_exec.set_flag_val(output_eicrecon_flag, output_file_path)
#         self._eicrecon_exec.set_flag_val(input_eicrecon_flag, input_file_path)
#         self._eicrecon_exec.set_flag_val(compact_eicrecon_flag, detector_build_path)
#         return self._eicrecon_exec.generate_cmd()
#
#     def npsim_filename(self) -> str:
#         return self._file_name("sim")
#
#     def eicrecon_filename(self) -> str:
#         return self._file_name("recon")
#
#     def _file_name(self, prefix : str) -> str:
#         if self.momentum_max == self.momentum_min:
#             momentum_str = f"mmt[{self.momentum_max}]"
#         else:
#             momentum_str = f"mmt[{self.momentum_max}_{self.momentum_min}]"
#         if self.eta_max:
#             angle_str = f"eta[{self.eta_max}_{self.eta_min}]"
#         else:
#             angle_str = f"theta[{self.theta_max}_{self.theta_min}]"
#         return f"{prefix}_{angle_str}_{momentum_str}.root"
#
#     def _populate_npsim_exec(self):
#         self._populate_exec(NPSIM_METADATA_KEY)
#
#     def _populate_eicrecon_exec(self):
#         self._populate_exec(EICRECON_METADATA_KEY)
#
#     def _populate_exec(self, exec_key):
#         try:
#             for key in self.keys():
#                 key_metadata = self.property_metadata(key)
#                 if exec_key in key_metadata.keys():
#                     key_flag = key_metadata[exec_key]
#                     key_value = self.property_value(key)
#                     if exec_key == NPSIM_METADATA_KEY:
#                         self._npsim_exec.set_flag_val(key_flag, key_value)
#                     elif exec_key == EICRECON_METADATA_KEY:
#                         self._eicrecon_exec.set_flag_val(key_flag, key_value)
#         except Exception as e:
#             raise e
#
#
# @dataclass
# class CommonSimulationConfig(SimulationConfig):
#
#     _is_common_config : bool = field(default=True, init=False)
#
#     def combine_sim_config(self, sim_config : SimulationConfig) -> SimulationConfig:
#
#         new_params = {}
#         for prop in self.keys():
#             curr_val = self.property_value(prop)
#             sim_val = sim_config.property_value(prop)
#             if not curr_val and sim_val:
#                 new_params[prop] = sim_val
#             elif curr_val and sim_val and isinstance(curr_val, list) and isinstance(sim_val, list):
#                 for elem in sim_val:
#                     curr_val.append(elem)
#                 new_params[prop] = curr_val
#             elif curr_val:
#                 new_params[prop] = curr_val
#         return SimulationConfig(**new_params)
#
#
# def npsim_command(common_config : CommonSimulationConfig, instance_config : SimulationConfig):
#     temp_config = common_config.combine_sim_config(instance_config)
#     return temp_config.npsim_cmd()
#
# def eicrecon_command(common_config : CommonSimulationConfig, instance_config : SimulationConfig):
#     temp_config = common_config.combine_sim_config(instance_config)
#     return temp_config.eicrecon_cmd()


# sim_test = SimulationConfig(
#     name="Test",
#     num_events=10000,
#     gun_particle=Particle.PionNeutral,
#     gun_distribution=GunDistribution.Eta,
#     momentum_max="10GeV",
#     momentum_min="10GeV",
#     eta_max=4,
#     eta_min=-4,
#     detector_build_path="tracking/epic_craterlake_tracking_only.xml"
# )




