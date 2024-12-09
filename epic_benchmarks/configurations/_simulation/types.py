from enum import Enum
import re
from epic_benchmarks.configurations.ranges import Range

#Simulation Enums

class Particle(Enum):
    PionNeutral = "pi"
    PionPlus = "pi+"
    PionNeg = "pi-"
    #TODO: Add all particles


class GunDistribution(Enum):
    Uniform = "uniform"
    Eta = "eta"
    #TODO: Add other distributions and assess their input requirements


class MomentumUnits(Enum):
    NoUnits = ""
    meV = "meV"
    eV = "eV"
    keV = "keV"
    MeV = "MeV"
    GeV = "GeV"
    TeV = "TeV"
    PeV = "PeV"

    @classmethod
    def regexPattern(cls):
        pattern = re.compile("|".join([str(unit for unit in cls)]))

    @classmethod
    def __repr__(cls):
        return f"[{", ".join([str(unit for unit in cls)])}]"


class ThetaRange(Range):
    Max = 180.0
    Min = -180.0
    ValueName = "Theta"
    ValueUnits = "Degrees"

class EtaRange(Range):
    Max = 100.0
    Min = -100.0
    ValueName = "Eta"

class MomentumRange(Range):
    Max = 1000000
    Min = 1
    ValueName = "Momentum"
    ValueUnits = "MeV"
