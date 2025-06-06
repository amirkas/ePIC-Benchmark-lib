from typing import Any, Optional
from ePIC_benchmarks.simulation.simulation_types import Momentum, GunDistribution
from ePIC_benchmarks.simulation.simulation_types.types import DistributionLimitType

#Formats the simulation name based on its momentum range and phase space range
def format_simulation_name(
        momentum_min : Optional[Momentum] =None,
        momentum_max : Optional[Momentum]=None,
        distribution_type :  GunDistribution = None,
        distribution_min :  DistributionLimitType=None,
        distribution_max :  DistributionLimitType=None) -> str:
    
    #Formats the momentum substring based on whether
    #momentum_min and/or momentum_max is provided
    momentum_min = str(momentum_min).replace('*', '')
    momentum_max = str(momentum_max).replace('*', '')
    if momentum_min is not None and momentum_max is None:
        momentum_str = f"{momentum_min}"
    elif momentum_max is not None and momentum_min is None:
        momentum_str = f"{momentum_max}"
    elif momentum_min == momentum_max:
        momentum_str = f"{momentum_min}"
    else:
        momentum_str = f"{momentum_min}_to_{momentum_max}"

    #Formats the phase space range substring
    distribution_type_str = distribution_type.value
    distribution_str = f"{distribution_type_str}_{distribution_min}_to_{distribution_max}"
    name_str = f"{distribution_str}_{momentum_str}"
    return name_str

#Casts a provided momentum value to an instance of Momentum
def validate_momentum_limit(momentum_value : Any) -> Momentum:

    return Momentum.to_quantity(momentum_value)

#Formats the name for a Simulation Config if one isn't provided.
def validate_name(
        name_value : str,
        momentum_min :  Optional[Momentum] =None,
        momentum_max :  Optional[Momentum]=None,
        distribution_type :  Optional[GunDistribution] = None,
        distribution_min :  Optional[DistributionLimitType]=None,
        distribution_max :  Optional[DistributionLimitType]=None) -> str:

    if name_value is None:
        assert momentum_min is not None or momentum_max is not None, "Momentum min or max must not be None"
        assert distribution_type is not None, "Distribution type must not be None"
        assert distribution_min is not None, "Distribution min must not be None"
        assert distribution_max is not None, "Distribution max must not be None"
        return format_simulation_name(
            momentum_min=momentum_min,
            momentum_max=momentum_max,
            distribution_type=distribution_type,
            distribution_min=distribution_min,
            distribution_max=distribution_max
        )
    elif isinstance(name_value, str):
        return name_value
    else:
        try:
            return str(name_value)
        except:
            err = f"Input for name has type '{type(name_value)}' which cannot be converted to a string"
            raise ValueError(err)

#Validates and formats the limits of a Simulation Config's momentum range
def validate_momentum_range(momentum_min : Optional[Momentum], momentum_max : Optional[Momentum]) -> None:

    err = None
    if momentum_min is None and momentum_max is None:
        err = f"No momentum provided. At least one limit for the momentum range must be provided."
    elif momentum_min is not None and momentum_max is not None:
        if momentum_min > momentum_max:
            err = (
                f"Minimum momentum '{momentum_min}' must be less" 
                f"than or equal to the maximum momentum '{momentum_max}'"
            )

    if err is not None:
        raise ValueError(err)
    
#Checks that the number of events is greater than 0
def validate_num_events(num_events : int) -> None:

    if num_events <= 0:
        err = f"Number of events to simulate cannot be 0 or negative. Got '{num_events}'"
        raise ValueError(err)

#Checks that the multiplicity is greater than 0  
def validate_multiplicity(multiplicity : float) -> None:

    if multiplicity <= 0.0:
        err = f"Multiplicity cannot be 0 or negative. Got '{multiplicity}'"
        raise ValueError(err)
    
#TODO: Add validation for gunEnabled = False


    