from enum import Enum
from pydantic import Field, AliasChoices, AliasPath

from epic_benchmarks.simulation.flags import NPSIM_METADATA_KEY, NpsimFlag
from epic_benchmarks.simulation.types import GunDistribution

class DistributionSettingsFields(Enum):

    DISTRIBUTION_TYPE_FIELD = Field(
        default=GunDistribution.Uniform,
        validate_default=True,
        json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.GunDistribution.value}
    )
    THETA_MIN_FIELD = Field(
        default=None,
        validation_alias=AliasChoices(
            'theta_min',
            'min_theta',
            AliasPath('theta_range', 0),
        ),
        json_schema_extra={
            NPSIM_METADATA_KEY : NpsimFlag.GunThetaMin.value
        },
    )
    THETA_MAX_FIELD = Field(
        default=None,
        validation_alias=AliasChoices(
            'theta_max',
            'max_theta',
            AliasPath('theta_range', 1),
        ),
        json_schema_extra={
            NPSIM_METADATA_KEY: NpsimFlag.GunThetaMax.value
        },
    )
    ETA_MIN_FIELD = Field(
        default=None,
        validation_alias=AliasChoices(
            'eta_min',
            'min_eta',
            AliasPath('eta_range', 0),
        ),
        json_schema_extra={
            NPSIM_METADATA_KEY: NpsimFlag.GunEtaMin.value
        },
    )
    ETA_MAX_FIELD = Field(
        default=None,
        validation_alias=AliasChoices(
            'eta_max',
            'max_eta',
            AliasPath('eta_range', 1),
        ),
        json_schema_extra={
            NPSIM_METADATA_KEY: NpsimFlag.GunEtaMax.value
        },
    )
    DISTRIBUTION_MIN_FIELD = Field(
        default=None,
        init=False
    )
    DISTRIBUTION_MAX_FIELD = Field(
        default=None,
        init=False
    )