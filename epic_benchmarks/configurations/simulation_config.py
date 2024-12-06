import re
import numbers
from dataclasses import dataclass

METADATA_DEFAULT = "default"
METADATA_TYPES = "types"

MAGNITUDE_SYMBOLS = ['z', 'a', 'f', 'p', 'n', 'u', 'm', 'k', 'M', 'G', 'T', 'P', 'E']
MOMENTUM_SUFFIX = "eV"
DEGREES_SUFFIX = "*degree"
THETA_STR = "theta"
ETA_STR = "eta"
GUN_DISTRIBUTIONS = ["uniform", "eta", "cos(theta)", "pseudorapidity", "ffbar"]
ANGLE_TYPES = ["theta", "eta"]

BENCHMARK_SIMULATION_CONFIG_KEY = "simulation_config"
BENCHMARK_SIMULATION_COMMON_KEY = "common"
BENCHMARK_SIMULATION_LIST_KEY = "simulations"
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
RECONSTRUCTION_FLAGS_KEY = "eicrecon_flags"

SIMULATION_KEYS = [
    SIMULATION_NAME_KEY,
    SIMULATION_BINS_KEY,
    SIMULATION_DETECTOR_KEY,
    SIMULATION_NUM_EVENTS_KEY,
    SIMULATION_ENABLE_GUN_KEY,
    SIMULATION_DISTRIBUTION_KEY,
    SIMULATION_PARTCILE_KEY,
    SIMULATION_MULTIPLICITY_KEY,
    SIMULATION_MOMENTUM_MAX_KEY,
    SIMULATION_MOMENTUM_MIN_KEY,
    SIMULATION_THETA_MAX_KEY,
    SIMULATION_THETA_MIN_KEY,
    SIMULATION_ETA_MAX_KEY,
    SIMULATION_ETA_MIN_KEY,
    RECONSTRUCTION_FLAGS_KEY,
]

argument_map = {
        "name" : SIMULATION_NAME_KEY,
        "detector_path" : SIMULATION_DETECTOR_KEY,
        "num_events" : SIMULATION_NUM_EVENTS_KEY,
        "enable_gun" : SIMULATION_ENABLE_GUN_KEY,
        "gun_distribution" : SIMULATION_DISTRIBUTION_KEY,
        "particle" : SIMULATION_PARTCILE_KEY,
        "multiplicity" : SIMULATION_MULTIPLICITY_KEY,
        "max_momentum" : SIMULATION_MOMENTUM_MAX_KEY,
        "min_momentum" : SIMULATION_MOMENTUM_MIN_KEY,
        "max_theta" : SIMULATION_THETA_MAX_KEY,
        "min_theta" : SIMULATION_THETA_MIN_KEY,
        "max_eta" : SIMULATION_ETA_MAX_KEY,
        "min_eta" : SIMULATION_ETA_MIN_KEY,
        "bin_names" : SIMULATION_BINS_KEY,
        "recon_flags" : RECONSTRUCTION_FLAGS_KEY
}

def format_theta(theta):

    if isinstance(theta, int):
        return "{angle}{suffix}".format(angle=theta, suffix=DEGREES_SUFFIX)
    if isinstance(theta, str):
        return

def format_momentum(momentum, units="GeV"):

    #Check if momentum is not a valid type
    if not (isinstance(momentum, str) or isinstance(momentum, numbers.Number)):
        raise Exception("Momentum must be represented by a number or a string",
                         "\nGiven type is {t}".format(t=type(momentum)))

    #if momentum is represented by a string, 
    #generate units from the suffix if the momentum is not entirely compromised of digits 
    if isinstance(momentum, str) and not momentum.isnumeric():
        #Generate suffix

        prefixes = re.findall(r'\d+', momentum)
        if len(prefixes) > 1:
            raise Exception("Incorrect format")
        prefix = prefixes[0]
        suffixes = re.findall(r"[{magnitudes}]?[eE][vV]".format(magnitudes="".join(MAGNITUDE_SYMBOLS)), momentum)
        if len(suffixes) > 1:
            raise Exception("Incorrect format")
        suffix = suffixes[0]
        if len(prefix) == 0:
            raise Exception("The value for momentum cannot be empty")
        if len(suffix) > 3:
            raise Exception("The units have an invalid format")
        momentum = prefix
            
    if isinstance(momentum, numbers.Number):

        suffixes = re.findall(r"[{magnitudes}]?[eE][vV]".format(magnitudes="".join(MAGNITUDE_SYMBOLS)), units)
        if len(suffixes) == 0 or len(suffixes) > 1:
            raise Exception("Incorrect format")
        units = suffixes[0]
        
    #check if units are valid
    if not len(units) == 3 and not len(units) == 2:
        raise Exception("Units must be either 2 or 3 characters long")
    if len(units) == 3:
        suffix = units.lower()[-2:]
        magnitude = units[-3]
    if len(units) == 2:
        suffix = units.lower()
        magnitude = ""
    if suffix != "ev":
        raise Exception("Units must be measured in eV")
    if magnitude != "" and magnitude not in MAGNITUDE_SYMBOLS:
        raise Exception("Magnitude must be one of the following: ", MAGNITUDE_SYMBOLS)
        
    return "{momentum}*{units_magnitude}{units}".format(
        momentum=momentum,
        units_magnitude=magnitude,
        units=MOMENTUM_SUFFIX)


class SimulationConfig:

    def __init__(self, load_simulation_config=None, simulation_name="", use_eta=False, use_bins=False, load_config_dict=None):

        
        for key in SIMULATION_KEYS:
            setattr(self, key, None)

        if load_simulation_config != None:
            if not isinstance(load_simulation_config, dict):
                raise Exception("Simulation config to load must be a Python dictionary")
            
            loaded_config = load_simulation_config
            loaded_keys = loaded_config.keys()
            setattr(self, "use_eta", False)
            setattr(self, "use_bins", False)
            if SIMULATION_ETA_MAX_KEY in loaded_keys or SIMULATION_ETA_MIN_KEY in loaded_keys:
                setattr(self, "use_eta", True)
            if SIMULATION_BINS_KEY in loaded_keys:
                setattr(self, "use_bins", True)
            for k, v in loaded_config.items():
                setattr(self, k, v)
            
        else:
            self.use_eta = use_eta
            self.use_bins = use_bins
            setattr(self, SIMULATION_NAME_KEY, simulation_name)

    def set_params(
        self, detector_path=None, num_events=None, enable_gun=None,
        gun_distribution=None, particle=None, multiplicity=None,
        max_momentum=None, min_momentum=None, max_theta=None,
        min_theta=None, max_eta=None, min_eta=None, bin_names=None, recon_flags=None):

        for key, value in locals().items():
            if key != "self":
                mapped_arg = argument_map[key]
                setattr(self, mapped_arg, value)
        
    def __setattr__(self, name, value):

        if value == None:
            return
        #Validate values and format them if necessary
        if name == SIMULATION_NAME_KEY:
            if len(name.strip()) == 0:
                return
        if name == SIMULATION_DETECTOR_KEY:
            #Checks to see if path is a string
            if not isinstance(value, str):
                print("Detector path must be a string")
                return
            #Check to see if detector path file extension is .xml
            if not value.endswith(".xml"):
                print('Detector path: "{path}" must point to an xml file (must end with .xml)'.format(value))
                return
        if name == SIMULATION_NUM_EVENTS_KEY:
            try:
                value = int(value)
            except:
                print("Number of events must be an integer or convertible to an integer")
                return
        if name == SIMULATION_ENABLE_GUN_KEY:
            if not isinstance(value, bool):
                print("Value must be a boolean")
        if name == SIMULATION_DISTRIBUTION_KEY:
            if value not in GUN_DISTRIBUTIONS:
                print("Distribution must be one of the following distributions: ", GUN_DISTRIBUTIONS)
                return
        if name == SIMULATION_PARTCILE_KEY:
            pass
        if name == SIMULATION_MULTIPLICITY_KEY:
            pass
        if name == SIMULATION_MOMENTUM_MAX_KEY:
            value = format_momentum(momentum=value)
        if name == SIMULATION_MOMENTUM_MIN_KEY:
            value = format_momentum(momentum=value)
        if name == SIMULATION_THETA_MAX_KEY:
            if self.use_eta:
                print("Use eta must be set to false to set a theta range")
                return
        if name == SIMULATION_THETA_MIN_KEY:
            if self.use_eta:
                print("Use eta must be set to false to set a theta range")
                return
        if name == SIMULATION_ETA_MAX_KEY:
            if not self.use_eta:
                print("Use eta must be set to True to set an eta range")
                return
        if name == SIMULATION_ETA_MIN_KEY:
            if not self.use_eta:
                print("Use eta must be set to True to set an eta range")
                return
        if name == SIMULATION_BINS_KEY:
            if not self.use_bins:
                print("Use bins attribute must be True to set bins")
        
        #After validation and formatting, set the attribute
        super().__setattr__(name, value)
        
    def get_config_dict(self):

        config = {}
        for attr, val in self.__dict__.items():
            if attr != "use_eta" and attr != "use_bins" and attr in SIMULATION_KEYS:
                config[attr] = val
        return config
                

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


class SimulationCommonConfig(SimulationConfig):

    def __init__(self, use_eta=False, use_bins=False):
        default_params = {
            SIMULATION_DETECTOR_KEY : DEFAULT_DETECTOR,
            SIMULATION_NUM_EVENTS_KEY : DEFAULT_NUM_EVENTS,
            SIMULATION_DISTRIBUTION_KEY : DEFAULT_GUN_DISTRIBUTION,
            SIMULATION_ENABLE_GUN_KEY : DEFAULT_ENABLE_GUN,
            SIMULATION_PARTCILE_KEY : DEFAULT_PARTICLE,
            SIMULATION_MULTIPLICITY_KEY : DEFAULT_MULTIPLICITY,
            SIMULATION_MOMENTUM_MAX_KEY : DEFAULT_MOMENTUM_MAX,
            SIMULATION_MOMENTUM_MIN_KEY : DEFAULT_MOMENTUM_MIN,
            SIMULATION_THETA_MAX_KEY : DEFAULT_THETA_MAX,
            SIMULATION_THETA_MIN_KEY : DEFAULT_THETA_MIN,
            SIMULATION_ETA_MAX_KEY : DEFAULT_ETA_MAX,
            SIMULATION_ETA_MIN_KEY : DEFAULT_ETA_MIN
        }
        super().__init__(simulation_name=None, use_eta=use_eta, use_bins=use_bins, load_config_dict=default_params)
        


CONFIG_TO_SIM_CMD = {
    SIMULATION_DETECTOR_KEY : "--compactFile ",
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

STRING_ARGUMENTS = [
    SIMULATION_PARTCILE_KEY,
    SIMULATION_MOMENTUM_MAX_KEY,
    SIMULATION_MOMENTUM_MIN_KEY,
    SIMULATION_ETA_MAX_KEY,
    SIMULATION_ETA_MIN_KEY,
    SIMULATION_THETA_MAX_KEY,
    SIMULATION_THETA_MIN_KEY
]

NON_STRING_ARGUMENTS = [
    SIMULATION_DETECTOR_KEY,
    SIMULATION_NUM_EVENTS_KEY,
    SIMULATION_DISTRIBUTION_KEY,
    SIMULATION_MULTIPLICITY_KEY
]

CONFIG_TO_RECON_CMD = {
    SIMULATION_DETECTOR_KEY : "-Pdd4hep:xml_files=",
    SIMULATION_NUM_EVENTS_KEY : "-Pjana:nevents="
}

RECON_OUTPUT_CMD = "-Ppodio:output_file="
RECON_NUM_THREADS_FLAG = "-Pnthreads="

def simulation_config_to_npsim_arg(output_filepath : str, common_config : SimulationCommonConfig, simulation_config : SimulationConfig, detector_path : str):
    common_dict = common_config.get_config_dict()
    sim_dict = simulation_config.get_config_dict()
    combined_dict = dict(common_dict.items() | sim_dict.items())
    cmd_str = "npsim "
    for key, value in combined_dict.items():
        if key != SIMULATION_NAME_KEY:
            if key == SIMULATION_ENABLE_GUN_KEY:
                cmd_str += "{arg} ".format(arg=CONFIG_TO_SIM_CMD[SIMULATION_ENABLE_GUN_KEY]) if combined_dict[key] else " "
            elif key == SIMULATION_DETECTOR_KEY:
                cmd_str += "{cmd}{detector}/{arg} ".format(cmd=CONFIG_TO_SIM_CMD[key], detector=detector_path, arg=value)
            elif key in NON_STRING_ARGUMENTS:
                cmd_str += "{cmd}{arg} ".format(cmd=CONFIG_TO_SIM_CMD[key], arg=value)
            elif key in STRING_ARGUMENTS:
                cmd_str += '{cmd}"{arg}" '.format(cmd=CONFIG_TO_SIM_CMD[key], arg=value)
    cmd_str += "--outputFile {output_path}".format(output_path=output_filepath)
    
    return cmd_str

def simulation_config_to_eicrecon_arg(input_filepath : str, output_filepath : str, common_config : SimulationCommonConfig, simulation_config : SimulationConfig, detector_path : str, nthreads=1):
    common_dict = common_config.get_config_dict()
    sim_dict = simulation_config.get_config_dict()
    combined_dict = dict(common_dict.items() | sim_dict.items())
    cmd_str = "eicrecon "
    cmd_str += "{cmd}{dir}/{detector} ".format(cmd=CONFIG_TO_RECON_CMD[SIMULATION_DETECTOR_KEY], dir=detector_path, detector=combined_dict[SIMULATION_DETECTOR_KEY])
    cmd_str += "{cmd}{events} ".format(cmd=CONFIG_TO_RECON_CMD[SIMULATION_NUM_EVENTS_KEY], events=combined_dict[SIMULATION_NUM_EVENTS_KEY])
    cmd_str += "{cmd}{output_path} ".format(cmd=RECON_OUTPUT_CMD, output_path=output_filepath)
    cmd_str += "{cmd}{num_threads} ".format(cmd=RECON_NUM_THREADS_FLAG, num_threads=nthreads)
    additional_flags = combined_dict[RECONSTRUCTION_FLAGS_KEY]
    if additional_flags is not None:
        if isinstance(additional_flags, str):
            cmd_str += f"{additional_flags} "
        elif isinstance(additional_flags, list) and len(additional_flags) > 0:
            flags = " ".join(additional_flags)
            cmd_str += f"{flags} "
        else:
            raise Exception("Additional flags must be either a string or a list of strings")
        
    # cmd_str += f"{RECON_NUM_THREADS_FLAG} "
    cmd_str += input_filepath
    return cmd_str

