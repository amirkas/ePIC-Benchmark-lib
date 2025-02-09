from typing import Any, Optional, List, TypeVar

from epic_benchmarks.simulation.simulation_types import GunDistribution, Angle, Eta, DistributionLimitType
from epic_benchmarks.simulation._quantity import Quantity


QuantityType = TypeVar('Quantity', bound=Quantity)

def validate_distribution_limit(input_value : Any, distribution_type : QuantityType) -> DistributionLimitType:

    if input_value is None:
        return input_value
    elif isinstance(input_value, distribution_type):
        return input_value
    else:
        try:
            formatted_value = distribution_type.to_quantity(input_value)
            return formatted_value
        except Exception as e:
            raise e
        
def validate_theta_limit(input_value : Any) -> Angle:

    return validate_distribution_limit(input_value, Angle)

def validate_eta_limit(input_value : Any) -> Eta:

    return validate_distribution_limit(input_value, Eta)

def validate_only_one_limit_type(
        minimum_limits : List[Optional[DistributionLimitType]],
        maximum_limits : List[Optional[DistributionLimitType]]) -> None:
    
    minimum_limit_none_cnt = minimum_limits.count(None)
    maximum_limit_none_cnt = maximum_limits.count(None)
    num_min_limits = len(minimum_limits) - minimum_limit_none_cnt
    min_err = None
    if num_min_limits > 1:
        min_err = f"Too many minimum limits provided. Only one minimum limit can be provided."
    elif num_min_limits == 0:
        min_err = f"No minimum limit provided. One minimum limit must be provided."

    num_max_limits = len(maximum_limits) - maximum_limit_none_cnt
    max_error = None
    if num_max_limits > 1:
        max_err = f"Too many maximum limits provided. Only one maximum limit can be provided."
    elif num_max_limits == 0:
        max_err = f"No maximum limit provided. One maximum limit must be provided."

    if min_err and max_err:
        err = f"{min_err}\n{max_err}"
        raise ValueError(err)
    elif min_err:
        raise ValueError(min_err)
    elif max_err:
        raise ValueError(max_err)

def validate_limit_matches_type(
        input_value : DistributionLimitType, distribution_type : GunDistribution) -> None:

    if not isinstance(input_value, distribution_type.limit_type):
        err = f"Input value '{input_value}' with type '{type(input_value)}' does not match the distribution limit type '{distribution_type.limit_type}'"
        raise ValueError(err)

def validate_both_limits_provided(min_limit : DistributionLimitType, max_limit : DistributionLimitType) -> None:
    
    both_none = min_limit is None and max_limit is None
    both_present = min_limit is not None and max_limit is not None
    if not both_none and not both_present:
        err = f"If either the minimum or maximum limit for a distribution type is provided, the other one must also be provided"
        raise ValueError(err)

def validate_limits_same_type(min_limit : DistributionLimitType, max_limit : DistributionLimitType) -> None:

    min_limit_type = type(min_limit)
    max_limit_type = type(max_limit)

    if min_limit_type != max_limit_type:
        err = f"Type for the minimum distribution limit '{min_limit_type}' does not match the type for the maximum distribution limit '{max_limit_type}'"
        raise ValueError(err)
    
def validate_only_one_limit_type(
        minimum_limits : List[Optional[DistributionLimitType]],
        maximum_limits : List[Optional[DistributionLimitType]]) -> None:
    
    minimum_limit_none_cnt = minimum_limits.count(None)
    maximum_limit_none_cnt = maximum_limits.count(None)
    num_min_limits = len(minimum_limits) - minimum_limit_none_cnt
    min_err = None
    if num_min_limits > 1:
        min_err = f"Too many minimum limits provided. Only one minimum limit can be provided."
    elif num_min_limits == 0:
        min_err = f"No minimum limit provided. One minimum limit must be provided."

    num_max_limits = len(maximum_limits) - maximum_limit_none_cnt
    max_err = None
    if num_max_limits > 1:
        max_err = f"Too many maximum limits provided. Only one maximum limit can be provided."
    elif num_max_limits == 0:
        max_err = f"No maximum limit provided. One maximum limit must be provided."

    if min_err and max_err:
        err = f"{min_err}\n{max_err}"
        raise ValueError(err)
    elif min_err:
        raise ValueError(min_err)
    elif max_err:
        raise ValueError(max_err)
    
def validate_limit_range(min_limit : DistributionLimitType, max_limit : DistributionLimitType, same_value_allowed=False) -> None:

    assert(type(min_limit) == type(max_limit))

    if same_value_allowed:
        range_allowed = min_limit <= max_limit
    else:
        range_allowed = min_limit < max_limit

    if range_allowed:
        return

    if same_value_allowed:
        err = f"Value for minimum limit '{min_limit}' must be less than or equal to the maximum limit '{max_limit}'"
    else:
        err = f"Value for minimum limit '{min_limit}' must be strictly less than the maximum limit '{max_limit}'"
    raise ValueError(err)