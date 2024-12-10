from epic_benchmarks.configurations._simulation.types import MomentumUnits, MomentumRange
import re
import numbers

ELECTRON_VOLTS_PATTERN = r'^([mkMGTP]?)(eV)'
MOMENTUM_PATTERN = MomentumUnits.regexPattern()
THETA_PATTERN = rf'^(\d+)(\*?)(degree)?$'


#Validate configuration values
def validateMomentum(momentum) -> bool:
    if not isinstance(momentum, numbers.Number) and not isinstance(momentum, str):
        raise Exception("Momentum must be a string or a number")

    allowed_units = [unit.value for unit in MomentumUnits]
    if isinstance(momentum, str):
        match = re.match(MOMENTUM_PATTERN, momentum)
        if not match:
            raise AttributeError("Momentum does not have a valid format.")
        if match and not MomentumRange.inRange(match.group(1)):
            raise AttributeError(f"Momentum is not in range of allowed momenta. Allowed range is {MomentumRange}")
        if momentum.isnumeric():
            momentum = float(momentum)
    # if isinstance(momentum, numbers.Number) and cls.momentum_units == MomentumUnits.NoUnits:
    #     raise AttributeError("If momentum is provided as a number, you must provide units")

    return True

def formatMomentum(momentum):

    if isinstance(momentum, str):
        match = re.match(MOMENTUM_PATTERN, momentum)
        assert match
        momentum_value = match.group(1)
        units = match.group(3)
        if len(units) == 0:
            units = "MeV"

    else:
        momentum_value = momentum
        units = "MeV" #TODO: Placeholder, add behaviour for input units
    return f"{momentum_value}*{units}"