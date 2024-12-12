from enum import Enum
import re
from dataclasses import dataclass, field
from typing import Optional


#Simulation Objects

class Particle(Enum):
    PionNeutral = "pi"
    PionPlus = "pi+"
    PionNeg = "pi-"
    #TODO: Add all particles

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
    def _regexPattern(cls):
        prefix = fr'^(\d+)(\*?)('
        suffix = fr')?$'
        units_pattern = "|".join([str(unit.value) for unit in cls if unit is not MomentumUnits.NoUnits])
        pattern = prefix + units_pattern + suffix
        return pattern

    @classmethod
    def __repr__(cls):
        return f"[{", ".join([str(unit for unit in cls)])}]"

@dataclass
class Momentum:

    magnitude : float = field(init=True)
    units : Optional[MomentumUnits] = field(default=MomentumUnits.GeV, init=True)

    def __repr__(self):
        return f"{self.magnitude}{self.units.value}"

class GunDistribution(Enum):
    Uniform = "uniform"
    Eta = "eta"
    #TODO: Add other distributions and assess their input requirements


#Detector Objects

class DetectorConfigType(Enum):

    SET = "set"
    ADD = "add"
    DELETE = "delete"

#Benchmark Objects

class EpicBranches(Enum):

    MAIN = "main"
    SVT_CURVED = "svt_curved"
    #TODO: Add branches of epic repository to access





DETECTOR_SET_CMD = "set"
DETECTOR_ADD_CMD = "add"
DETECTOR_DELETE_CMD = "delete"
DETECTOR_CONFIG_TYPES = (DETECTOR_SET_CMD, DETECTOR_ADD_CMD, DETECTOR_DELETE_CMD)
DEFAULT_BRANCH = "main"

MAGNITUDE_SYMBOLS = ['z', 'a', 'f', 'p', 'n', 'u', 'm', 'k', 'M', 'G', 'T', 'P', 'E']
MOMENTUM_SUFFIX = "eV"
DEGREES_SUFFIX = "*degree"
THETA_STR = "theta"
ETA_STR = "eta"
GUN_DISTRIBUTIONS = ["uniform", "eta", "cos(theta)", "pseudorapidity", "ffbar"]
ANGLE_TYPES = ["theta", "eta"]

BENCHMARK_SUITE_NAME_KEY = "benchmark_suite_name"
BENCHMARK_LIST_KEY = "benchmarks"

NAME_KEY = "name"
REPO_BRANCH_KEY = "repository_branch"

DETECTOR_CONFIG_KEY = "detector_config"
DETECTOR_FILE_KEY = "file"
DETECTOR_TYPE_KEY = "type"
DETECTOR_NAME_KEY = "detector_name"
DETECTOR_MODULE_KEY = "module_name"
DETECTOR_MODULE_COMPONENT_KEY = "module_component"
DETECTOR_ATTRIBUTE_KEY = "attribute"
DETECTOR_VALUE_KEY = "value"
DETECTOR_ELEM_SPECIFIERS = [DETECTOR_NAME_KEY, DETECTOR_MODULE_KEY, DETECTOR_MODULE_COMPONENT_KEY]

SIMULATION_CONFIG_KEY = "simulation_config"
SIMULATION_COMMON_KEY = "common"
SIMULATION_LIST_KEY = "simulations"
SIMULATION_NAME_KEY = "name"
SIMULATION_BINS_KEY = "bin_names"
SIMULATION_DETECTOR_KEY = "detector_path"
SIMULATION_NUM_EVENTS_KEY = "num_events"
SIMULATION_ENABLE_GUN_KEY = "enable_gun"
SIMULATION_DISTRIBUTION_KEY = "gun_distribution"
SIMULATION_PARTCILE_KEY = "particle"
SIMULATION_MULTIPLICITY_KEY = "multiplicity"
SIMULATION_MOMENTUM_MAX_KEY = "momentum_max"
SIMULATION_MOMENTUM_MIN_KEY = "momentum_min"
SIMULATION_THETA_MAX_KEY = "theta_max"
SIMULATION_THETA_MIN_KEY = "theta_min"
SIMULATION_ETA_MAX_KEY = "eta_max"
SIMULATION_ETA_MIN_KEY = "eta_min"


DEFAULT_DETECTOR = None
DEFAULT_NUM_EVENTS = "100"
DEFAULT_ENABLE_GUN = True
DEFAULT_GUN_DISTRIBUTION = "uniform"
DEFAULT_PARTICLE = "pi+"
DEFAULT_MULTIPLICITY = 1
DEFAULT_MOMENTUM_MAX = "10*GeV"
DEFAULT_MOMENTUM_MIN = "10*GeV"
DEFAULT_THETA_MAX = "130*degree"
DEFAULT_THETA_MIN = "-130*degree"
DEFAULT_ETA_MAX = "4"
DEFAULT_ETA_MIN = "-4"

XPATH_DETECTOR_TAG = "detector"
XPATH_DETECTOR_NAME_ATTR = "name"
XPATH_MODULE_TAG = "module"
XPATH_MODULE_NAME_ATTR = "name"
XPATH_COMPONENT_TAG = "module_component"
XPATH_COMPONENT_NAME_ATTR = "name"

CONFIG_TO_SIM_CMD = {
    SIMULATION_DETECTOR_KEY : "--compactFile $DETECTOR_PATH/",
    SIMULATION_NUM_EVENTS_KEY : "--numberOfEvents ",
    SIMULATION_ENABLE_GUN_KEY : "--enableGun",
    SIMULATION_DISTRIBUTION_KEY : "--gun.distribution ",
    SIMULATION_PARTCILE_KEY : "--gun.particle ",
    SIMULATION_MOMENTUM_MAX_KEY : "--gun.momentumMax ",
    SIMULATION_MOMENTUM_MIN_KEY : "--gun.momentumMin ",
    SIMULATION_THETA_MAX_KEY : "--gun.thetaMax ",
    SIMULATION_THETA_MIN_KEY : "--gun.thetaMin ", 
    SIMULATION_ETA_MAX_KEY : "--gun.etaMax ",
    SIMULATION_ETA_MIN_KEY : "--gun.etaMin ",
    SIMULATION_MULTIPLICITY_KEY : "--gun.multiplicity "
}

CONFIG_TO_RECON_CMD = {
    SIMULATION_DETECTOR_KEY : "-Pdd4hep:xml_files=$DETECTOR_PATH/",
    SIMULATION_NUM_EVENTS_KEY : "-Pjana:nevents="
}

RECON_OUTPUT_CMD = "-Ppodio:output_file="