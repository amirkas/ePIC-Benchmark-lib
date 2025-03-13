from typing import Any, Optional, List, TypeVar

from ePIC_benchmarks.simulation.simulation_types import GunDistribution, Angle, Eta, DistributionLimitType
from ePIC_benchmarks.simulation._quantity import Quantity


QuantityType = TypeVar('Quantity', bound=Quantity)

#Validates and formats the provided limits of the provided phase space (distribution type).
def validate_distribution_limit(input_value : Any, distribution_limit_type : QuantityType) -> DistributionLimitType:

    #Returns None if the input value is None (not provided)
    if input_value is None:
        return input_value
    #If the input value is a distribution limit type, return it.
    elif isinstance(input_value, distribution_limit_type):
        return input_value
    #If the input is not a distribution limit type, attempt to cast it
    #to the distribution limit type associated with the provided phase space
    #If it cannot be cast, catch and throw the error thrown by the casting method
    else:
        try:
            formatted_value = distribution_limit_type.to_quantity(input_value)
            return formatted_value
        except Exception as e:
            raise e
        
#Validates and formats a Uniform Phase space limit
def validate_theta_limit(input_value : Any) -> Angle:

    return validate_distribution_limit(input_value, Angle)

#Validates and formats an Eta Phase space limit
def validate_eta_limit(input_value : Any) -> Eta:

    return validate_distribution_limit(input_value, Eta)

#Ensures only one of the distribution ranges (Theta or Eta) is provided.
def validate_only_one_limit_type(
        minimum_limits : List[Optional[DistributionLimitType]],
        maximum_limits : List[Optional[DistributionLimitType]]) -> None:
    
    #Counts the number of none values for a
    #model's distribution minimum / maximum phase space ranges
    minimum_limit_none_cnt = minimum_limits.count(None)
    maximum_limit_none_cnt = maximum_limits.count(None)

    #Checks that only 1 minimum phase space limit is not None
    #Formats an error if more than 1 is not None
    num_min_limits = len(minimum_limits) - minimum_limit_none_cnt
    min_err = None
    if num_min_limits > 1:
        min_err = f"Too many minimum limits provided. Only one minimum limit can be provided."
    elif num_min_limits == 0:
        min_err = f"No minimum limit provided. One minimum limit must be provided."

    #Checks that only 1 maximum phase space limit is not None
    #Formats an error if more than 1 is not None
    num_max_limits = len(maximum_limits) - maximum_limit_none_cnt
    max_error = None
    if num_max_limits > 1:
        max_err = f"Too many maximum limits provided. Only one maximum limit can be provided."
    elif num_max_limits == 0:
        max_err = f"No maximum limit provided. One maximum limit must be provided."

    #Throws the formatted errors
    if min_err and max_err:
        err = f"{min_err}\n{max_err}"
        raise ValueError(err)
    elif min_err:
        raise ValueError(min_err)
    elif max_err:
        raise ValueError(max_err)

#Ensures the provided distribution range matches the distribution type
#Theta Ranges -> Uniform Distribution Type
#Eta ranges -> Eta Distribution Type
def validate_limit_matches_type(
        input_value : DistributionLimitType, distribution_type : GunDistribution) -> None:

    #If the provided phase space range limits do not
    # match the provided phase space, throw an error
    if not isinstance(input_value, distribution_type.limit_type):
        err = (
            f"Input value '{input_value}' with type '{type(input_value)}'"
            f" does not match the distribution limit type '{distribution_type.limit_type}'"
        )
        raise ValueError(err)

#Ensures that both the minimum and maximum limits for a phase space range is provided
def validate_both_limits_provided(min_limit : DistributionLimitType, max_limit : DistributionLimitType) -> None:
    
    both_none = min_limit is None and max_limit is None
    both_present = min_limit is not None and max_limit is not None

    #If both the phase space limits are not provided, throw an error
    if not both_none and not both_present:
        err = (
            "If either the minimum or maximum limit for a distribution"
            " type is provided, the other one must also be provided"
        )
        raise ValueError(err)

#Ensures that both the provided minimum and maximum limits belong to the same Phase space 
def validate_limits_same_type(min_limit : DistributionLimitType, max_limit : DistributionLimitType) -> None:

    min_limit_type = type(min_limit)
    max_limit_type = type(max_limit)

    #If the phase space range limits do not have the same type, throw an error
    if min_limit_type != max_limit_type:
        err = (
            f"Type for the minimum distribution limit '{min_limit_type}' does"
            f" not match the type for the maximum distribution limit '{max_limit_type}'"
        )
        raise ValueError(err)

#Ensures that the phase space range and its constituent limits are valid
def validate_limit_range(min_limit : DistributionLimitType, max_limit : DistributionLimitType, same_value_allowed=False) -> None:

    assert(type(min_limit) == type(max_limit))

    #Process the minimum and maximum comparison differently if they are allowed to have the same value
    if same_value_allowed:
        range_allowed = min_limit <= max_limit
    else:
        range_allowed = min_limit < max_limit

    #If the range is not permissible, throw an error
    if not range_allowed:

        if same_value_allowed:
            err = (
                f"Value for minimum limit '{min_limit}' must be less"
                f" than or equal to the maximum limit '{max_limit}'"
            )
        else:
            err = (
                f"Value for minimum limit '{min_limit}' must be"
                f" strictly less than the maximum limit '{max_limit}'"
            )
        raise ValueError(err)