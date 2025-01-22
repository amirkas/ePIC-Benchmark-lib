from typing import Optional, Any, Self, Union
from pydantic import (
    BaseModel, ValidationInfo, Field,
    field_serializer, field_validator,
    model_validator, AliasChoices, AliasPath
)
from epic_benchmarks.simulation.types import Angle, Eta
from epic_benchmarks.simulation.types import GunDistribution, DistributionLimitType
from epic_benchmarks.simulation._utils import validate_enum
import epic_benchmarks.simulation.distribution._validators as distribution_validators

class DistributionSettings(BaseModel):

    distribution_type : GunDistribution = Field(default=GunDistribution.Uniform, validate_default=True)
    theta_min : Optional[Angle] = Field(
        default=None,
        validation_alias=AliasChoices(
            'theta_min',
            'min_theta',
            AliasPath('theta_range', 0),
        ),
    )
    theta_max : Optional[Angle] = Field(
        default=None,
        validation_alias=AliasChoices(
            'theta_max',
            'max_theta',
            AliasPath('theta_range', 1),
        ),
    )
    eta_min : Optional[Eta] = Field(
        default=None,
        validation_alias=AliasChoices(
            'eta_min',
            'min_eta',
            AliasPath('eta_range', 0),
        ),
    )
    eta_max : Optional[Eta] = Field(
        default=None,
        validation_alias=AliasChoices(
            'eta_max',
            'max_eta',
            AliasPath('eta_range', 1),
        ),
    )
    distribution_min : Optional[DistributionLimitType] = Field(default=None, init=False)
    distribution_max : Optional[DistributionLimitType] = Field(default=None, init=False)
    
    @field_validator('distribution_type', mode='after')
    def validate_distribution_enum(cls, value : Any) -> GunDistribution:        
        try:
            return validate_enum(value, GunDistribution)
        except Exception as e:
            raise e


    #Returns correctly formatted Theta limits or raises an error if format could not be complete
    @field_validator('theta_min', 'theta_max', mode='before')
    def format_theta_limit_values(cls, theta_value : Any) -> Optional[Angle]:
        try:
            return distribution_validators.validate_theta_limit(theta_value)
        except Exception as e:
            raise e
    
    #Returns correctly formatted Eta limits or raises an error if format could not be complete
    @field_validator('eta_min', 'eta_max', mode='before')
    def format_eta_limit_values(cls, eta_value : Any) -> Optional[Eta]:
        try:
            return distribution_validators.validate_eta_limit(eta_value)
        except Exception as e:
            raise e
    
    #Checks whether a provided limit matches the given distribution type
    @field_validator('theta_min', 'theta_max', 'eta_min', 'eta_max', mode='after')
    def check_limits_matches_distribution(
        cls, limit_value : Any,
        validation_info : ValidationInfo) -> Optional[DistributionLimitType]:

        if limit_value is not None:
            try:
                distribution_type = validation_info.data["distribution_type"]
                #Validator raises error if non-null limit value doesn't match the provided distribution type
                distribution_validators.validate_limit_matches_type(
                    input_value=limit_value,
                    distribution_type=distribution_type
                )
            except Exception as e:
                raise e
        return limit_value

    @field_validator('distribution_min', mode='after')
    def set_distribution_min(cls, value : Any, info : ValidationInfo) -> DistributionLimitType:

        theta_min = info.data['theta_min']
        eta_min = info.data['eta_min']
        if theta_min is not None:
            return theta_min
        elif eta_min is not None:
            return eta_min
        else:
            return None
        
    @field_validator('distribution_max', mode='after')
    def set_distribution_max(cls, value : Any, info : ValidationInfo) -> DistributionLimitType:

        theta_max = info.data['theta_max']
        eta_max = info.data['eta_max']
        if theta_max is not None:
            return theta_max
        elif eta_max is not None:
            return eta_max
        else:
            return None

    #Checks whether both limits of a given distribution type are provided
    @model_validator(mode='after')
    def check_both_limits_provided(self) -> Self:

        try:
            if self.theta_min or self.theta_max:
                distribution_validators.validate_both_limits_provided(self.theta_min, self.theta_max)
            if self.eta_min or self.eta_max:
                distribution_validators.validate_both_limits_provided(self.eta_min, self.eta_max)
        except Exception as e:
            raise e
        return self

    #Checks whether both limits are the same type
    @model_validator(mode='after')
    def check_both_limits_have_same_type(self) -> Self:

        try:
            if self.theta_min or self.theta_max:
                distribution_validators.validate_limits_same_type(self.theta_min, self.theta_max)
            if self.eta_min or self.eta_max:
                distribution_validators.validate_limits_same_type(self.eta_min, self.eta_max)
        except Exception as e:
            raise e
        return self

    #Checks whether only one limit range is provided
    @model_validator(mode='after')
    def check_only_one_range(self) -> Self:

        min_limits = [self.theta_min, self.eta_min]
        max_limits = [self.theta_max, self.eta_max]
        try:
            distribution_validators.validate_only_one_limit_type(
                minimum_limits=min_limits,
                maximum_limits=max_limits
            )
        except Exception as e:
            raise e
        return self

    #Checks if the distribution range is valid by comparing the minimum limit to the maximum limit
    @model_validator(mode='after')
    def check_distribution_range(self) -> Self:

        try:
            if self.theta_min or self.theta_max:
                distribution_validators.validate_limit_range(self.theta_min, self.theta_max)
            if self.eta_min or self.eta_max:
                distribution_validators.validate_limit_range(self.eta_min, self.eta_max)
        except Exception as e:
            raise e
        return self
    
    @field_serializer('distribution_type')
    def serialize_type(cls, dist_type : Union[str, GunDistribution]):

        if isinstance(dist_type, GunDistribution):
            return dist_type.value
        else:
            return dist_type


    
    


