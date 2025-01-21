from enum import Enum

from pydantic import Field, AliasChoices, AliasPath

from epic_benchmarks.simulation.types import Particle
from epic_benchmarks.simulation.flags import NPSIM_METADATA_KEY, EICRECON_METADATA_KEY, NpsimFlag, EicreconFlag

class SimulationSettingsFields(Enum):

    NUM_EVENTS_FIELD = Field(
        json_schema_extra={
            NPSIM_METADATA_KEY : NpsimFlag.NumEvents.value,
            EICRECON_METADATA_KEY : EicreconFlag.NumEvents.value,
        },
        description="Number of events to simulate",
    )
    MOMENTUM_MIN_FIELD = Field(
            validation_alias=AliasChoices(
                'momentum_min',
                'min_momentum',
                'momentum',
                AliasPath('momentum_range', 0),
                AliasPath('momenta', 0)
            ),
            json_schema_extra={ NPSIM_METADATA_KEY : NpsimFlag.GunMomentumMin.value },
            description="Minimum momentum value (or static momentum value)",
    )
    MOMENTUM_MAX_FIELD = Field(
        validation_alias=AliasChoices(
            'momentum_max',
            'max_momentum',
            'momentum',
            AliasPath('momentum_range', 0),
            AliasPath('momenta', 0)
        ),
        json_schema_extra={NPSIM_METADATA_KEY: NpsimFlag.GunMomentumMax.value},
        description="Maximum momentum value (or static momentum value)",
    )
    NAME_FIELD = Field(default=None, description="Name of the simulation")
    ENABLE_GUN_FIELD = Field(
        default=True,
        json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.EnableGun.value}
    )
    PARTICLE_FIELD = Field(
        default=Particle.PionNeutral,
        json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.GunParticle.value}
    )
    MULTIPLICITY_FIELD = Field(
        default=1.0,
        json_schema_extra={NPSIM_METADATA_KEY : NpsimFlag.GunMultiplicity.value}
    )
    DETECTOR_FILE_RELATIVE_PATH_FIELD= Field(exclude=True)
    FILE_PATHS_FIELD = Field(default=None, exclude=True, init=False)


    