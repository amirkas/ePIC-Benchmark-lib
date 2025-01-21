
from functools import cached_property
from typing import Optional, Any, Self, Dict, Union
from pydantic import BaseModel, ConfigDict, ValidationInfo, computed_field, field_serializer, field_validator, model_serializer, model_validator
from pyparsing import Opt

from epic_benchmarks.simulation.types import Angle, Eta
from epic_benchmarks.simulation.distribution._fields import DistributionSettingsFields
from epic_benchmarks.simulation.types import GunDistribution, DistributionLimitType
import epic_benchmarks.simulation.distribution._validators as distribution_validators

class DistributionSettings(BaseModel):

    distribution_type : GunDistribution = DistributionSettingsFields.DISTRIBUTION_TYPE_FIELD.value
    theta_min : Optional[Angle] = DistributionSettingsFields.THETA_MIN_FIELD.value
    theta_max : Optional[Angle] = DistributionSettingsFields.THETA_MAX_FIELD.value
    eta_min : Optional[Eta] = DistributionSettingsFields.ETA_MIN_FIELD.value
    eta_max : Optional[Eta] = DistributionSettingsFields.ETA_MAX_FIELD.value
    distribution_min : Optional[DistributionLimitType] = DistributionSettingsFields.DISTRIBUTION_MIN_FIELD.value
    distribution_max : Optional[DistributionLimitType] = DistributionSettingsFields.DISTRIBUTION_MAX_FIELD.value
    


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

        try:
            if limit_value is not None:
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


    #Custom model serializer to ensure only provided ranges are serialized
    @model_serializer(mode='wrap')
    def serialize_distribution_settings(self, handler) -> Dict[str, Any]:
        serialized_dict = {'distribution_type' : self.distribution_type.value}
        if self.theta_min is not None and self.theta_max is not None:
            serialized_dict["theta_min"] = str(self.theta_min)
            serialized_dict["theta_max"] = str(self.theta_max)
        elif self.eta_min is not None and self.eta_max is not None:
            serialized_dict["eta_min"] = str(self.eta_min)
            serialized_dict["eta_max"] = str(self.eta_max)
        #TODO: Add serialization for supported distributions in the future.
        return serialized_dict



    
    


