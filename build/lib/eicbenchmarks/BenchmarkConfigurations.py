import yaml
import os
import numbers
import re
from eicbenchmarks._constants import *

CWD = os.getcwd()

def has_key(dictionary, key):
    if not isinstance(dictionary, dict):
        print("Argument for dictionary is not a dictionary")
        return
    return key in dictionary.keys()

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
        # suffix_len = 0
        # for c in momentum[::-1]:
        #     if not c.isalpha():
        #         break
        #     if suffix_len == 3 and c != '*':
        #         raise Exception("Suffix cannot be more than 3 characters")
        #     elif suffix_len <=3 and c == "*":
        #         break
        #     suffix = c + suffix
        #     suffix_len += 1
        units = suffix
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




    
class DetectorConfig:

    def __init__(
            self, config_type, detector_file_name=None,
            detector_element_name=None, module_name=None,
            module_component_name=None, attribute=None, value=None
            ):
        
        if detector_file_name == None:
            raise Exception("Filename for detector must be specified")

        if not isinstance(config_type, str):
            raise Exception("Config type must be a string")
        
        #User must specify at least one of the following for any detector config type:
        #   - 'detector_name', 
        #   - 'module_name'
        #   - 'module_component'

        if detector_element_name == None and module_name == None and module_component_name == None:
            raise Exception("Access specifier must be an argument to find elements to update")
        
        if attribute == None:
            raise Exception("'attribute' must be an argument")

        if config_type.lower() == DETECTOR_CONFIG_TYPES[2]:
            return self.remove_config(
                file=detector_file_name,
                detector_name=detector_element_name,
                module_name=module_name,
                module_component=module_component_name,
                attribute=attribute
                )

        elif config_type.lower() == DETECTOR_CONFIG_TYPES[0]:
            if value == None:
                raise Exception("'value' must be an argument for 'set' config type")
            return self.set_config(
                file=detector_file_name,
                detector_name=detector_element_name,
                module_name=module_name,
                module_component=module_component_name,
                attribute=attribute,
                value=value
                )

        elif config_type.lower() == DETECTOR_CONFIG_TYPES[1]:
            if value == None:
                raise Exception("'value' must be an argument for 'add' config types")
            return self.add_config(
                file=detector_file_name,
                detector_name=detector_element_name,
                module_name=module_name,
                module_component=module_component_name,
                attribute=attribute,
                value=value
            )

        else:
            raise Exception("config type must be one of the following: ", DETECTOR_CONFIG_TYPES)

    def get_config(self):
        return self.config

    def set_config(self, file, detector_name, module_name, module_component, attribute, value):
        self.config = {
            DETECTOR_FILE_KEY : file,
            DETECTOR_TYPE_KEY : DETECTOR_CONFIG_TYPES[0]
        }
        if not detector_name == None:
            self.config[DETECTOR_NAME_KEY] = detector_name
        if not module_name == None:
            self.config[DETECTOR_MODULE_KEY] = module_name
        if not module_component == None:
            self.config[DETECTOR_MODULE_COMPONENT_KEY] = module_component
        self.config[DETECTOR_ATTRIBUTE_KEY] = attribute
        self.config[DETECTOR_VALUE_KEY] = value
        

    def add_config(self, file, detector_name, module_name, module_component, attribute, value):
        self.config = {
            DETECTOR_FILE_KEY : file,
            DETECTOR_TYPE_KEY : DETECTOR_CONFIG_TYPES[1]
        }
        if not detector_name == None:
            self.config[DETECTOR_NAME_KEY] = detector_name
        if not module_name == None:
            self.config[DETECTOR_MODULE_KEY] = module_name
        if not module_component == None:
            self.config[DETECTOR_MODULE_COMPONENT_KEY] = module_component
        self.config[DETECTOR_ATTRIBUTE_KEY] = attribute
        self.config[DETECTOR_VALUE_KEY] = value

    def remove_config(self, file, detector_name, module_name, module_component, attribute):
        self.config = {
            DETECTOR_FILE_KEY : file,
            DETECTOR_TYPE_KEY : DETECTOR_CONFIG_TYPES[2]
        }
        if not detector_name == None:
            self.config[DETECTOR_NAME_KEY] = detector_name
        if not module_name == None:
            self.config[DETECTOR_MODULE_KEY] = module_name
        if not module_component == None:
            self.config[DETECTOR_MODULE_COMPONENT_KEY] = module_component
        self.config[DETECTOR_ATTRIBUTE_KEY] = attribute


class SimulationConfig:

    def __init__(self, simulation_name="", use_eta=False, use_bins=False):

        self.use_eta = use_eta
        self.use_bins = use_bins
        self.config={}
        self.set_name(simulation_name)

    def get_config(self):
        return self.config

    def set_params(
        self, detector_path=None, num_events=None, gun_enabled=None,
        gun_distribution=None, particle=None, multiplicity=None,
        max_momentum=None, min_momentum=None, max_theta=None,
        min_theta=None, max_eta=None, min_eta=None, bin_names=None):

        self.set_detector_path(detector_path)
        self.set_num_events(num_events)
        self.set_gun_enabled(gun_enabled)
        self.set_gun_distribution(gun_distribution)
        self.set_particle(particle)
        self.set_multiplicity(multiplicity)
        self.set_max_momentum(max_momentum)
        self.set_min_momentum(min_momentum)
        if self.use_eta:
            self.set_eta_max(max_eta)
            self.set_eta_min(min_eta)
        else:
            self.set_theta_max(max_theta)
            self.set_theta_min(min_theta)

    
    def set_name(self, name):
        if name == None:
            return
        #do not add simulation name key-value pair if name is empty
        if len(name.strip()) == 0:
            return
        self.name = name
        self.config[SIMULATION_NAME_KEY] = name

    def set_detector_path(self, detector_path):
        if detector_path == None:
            return
        #Checks to see if path is a string
        if not isinstance(detector_path, str):
            print("Detector path must be a string")
            return
        #Check to see if detector path file extension is .xml
        if not detector_path.endswith(".xml"):
            print('Detector path: "{path}" must point to an xml file (must end with .xml)'.format(detector_path))
            return
        #TODO: Check if detector_path will be available after configurations are compiled
        
        self.config[SIMULATION_DETECTOR_KEY] = detector_path
        
    def set_num_events(self, num_events):
        if num_events == None:
            return 
        try:
            self.config[SIMULATION_NUM_EVENTS_KEY] = int(num_events)
        except:
            print("Number of events must be an integer or convertible to an integer")

    def set_gun_enabled(self, gun_enabled_bool):
        if gun_enabled_bool == None:
            return
        self.config[SIMULATION_ENABLE_GUN_KEY] = gun_enabled_bool

    def enable_gun(self):
        
        self.config[SIMULATION_ENABLE_GUN_KEY] = True

    def disable_gun(self):
        self.config[SIMULATION_ENABLE_GUN_KEY] = False

    def set_gun_distribution(self, distribution):
        if distribution == None:
            return
        if distribution not in GUN_DISTRIBUTIONS:
            print("Distribution must be one of the following distributions: ", GUN_DISTRIBUTIONS)
            return
        self.config[SIMULATION_DISTRIBUTION_KEY] = distribution

    def set_particle(self, particle):
        if particle == None:
            return
        self.config[SIMULATION_PARTCILE_KEY] = particle
    
    def set_multiplicity(self, multiplicity):
        if multiplicity == None:
            return
        self.config[SIMULATION_MULTIPLICITY_KEY] = multiplicity

    def set_max_momentum(self, max_momentum, units="GeV"):
        if max_momentum == None:
            return
        self.config[SIMULATION_MOMENTUM_MAX_KEY] = format_momentum(max_momentum, units)
    
    def set_min_momentum(self, min_momentum, units="GeV"):
        if min_momentum == None:
            return
        self.config[SIMULATION_MOMENTUM_MIN_KEY] = format_momentum(min_momentum, units)

    def set_angle_type(self, angle_type):
        if angle_type not in ANGLE_TYPES:
            print("Angle type must be '{theta_type}' or '{eta_type}'".format(theta_type=ANGLE_TYPES[0], eta_type=ANGLE_TYPES[1]))
        self.use_eta = True if angle_type == "theta" else False
        if self.use_eta:
            del self.config[SIMULATION_THETA_MAX_KEY]
            del self.config[SIMULATION_THETA_MIN_KEY]
        else:
            del self.config[SIMULATION_ETA_MAX_KEY]
            del self.config[SIMULATION_ETA_MIN_KEY]

    def set_theta_max(self, max_theta):
        if max_theta == None:
            return
        #Dont set theta if the simulation is set to use eta
        if self.use_eta:
            print("Cannot set theta parameters when simulation is set to use eta parameters")
            print("Use set_angle_type('{theta_type}') to set the simulation to use theta parameters".format(theta_type=ANGLE_TYPES[0]))
            return
        
        self.config[SIMULATION_THETA_MAX_KEY] = format_theta(max_theta)

    def set_theta_min(self, min_theta):
        if min_theta == None:
            return
        #Dont set theta if the simulation is set to use eta
        if self.use_eta:
            print("Cannot set theta parameters when simulation is set to use eta parameters")
            print("Use set_angle_type('{eta_type}') to set the simulation to use theta parameters".format(eta_type=ANGLE_TYPES[1]))
            return
        self.config[SIMULATION_THETA_MIN_KEY] = format_theta(min_theta)


    def set_eta_max(self, max_eta):
        if max_eta == None:
            return
        if not self.use_eta:
            print("Cannot set eta parameters when simulation is set to use theta parameters")
            print("Use set_angle_type('eta') to set the simulation to use eta parameters")
            return
        self.config[SIMULATION_ETA_MAX_KEY] = max_eta

    def set_eta_min(self, min_eta):
        if min_eta == None:
            return
        if not self.use_eta:
            print("Cannot set eta parameters when simulation is set to use theta parameters")
            print("Use set_angle_type('eta') to set the simulation to use eta parameters")
            return
        self.config[SIMULATION_ETA_MIN_KEY] = min_eta

    def set_bin_names(self, bins):
        if not self.use_bins:
            print("Must enable bins before setting them.")
            return
        if not isinstance(bins, list):
            print("Bins must be a list of strings or numbers representing each bin name")
        for bin in bins:
            if not isinstance(bin, (numbers.Number, str)):
                print("Bin: {b} does not have a valid bin format.".format(b=bin),
                      "It must be a numeric or string")
        self.config[SIMULATION_BINS_KEY] = bins


class SimulationCommonConfig(SimulationConfig):

    def __init__(self, use_eta=False, use_bins=False):
        super().__init__(simulation_name="", use_eta=use_eta, use_bins=use_bins)
        default_params = {
            "detector_path": DEFAULT_DETECTOR,
            "num_events": DEFAULT_NUM_EVENTS,
            "gun_distribution": DEFAULT_GUN_DISTRIBUTION,
            "gun_enabled": DEFAULT_ENABLE_GUN,
            "particle": DEFAULT_PARTICLE,
            "multiplicity": DEFAULT_MULTIPLICITY,
            "max_momentum": DEFAULT_MOMENTUM_MAX,
            "min_momentum": DEFAULT_MOMENTUM_MIN,
            "max_theta": DEFAULT_THETA_MAX,
            "min_theta": DEFAULT_THETA_MIN,
            "max_eta": DEFAULT_ETA_MAX,
            "min_eta": DEFAULT_ETA_MIN
        }
        self.set_params(**default_params)
        
class BenchmarkConfig:

    def __init__(self, benchmark_name="benchmark", repo_branch=DEFAULT_BRANCH, detector_configs=[], common_simulation_config=SimulationCommonConfig(), simulation_configs=[]):

        #Check if input objects have the correct type:
        for detector_config in detector_configs:
            if not isinstance(detector_config, DetectorConfig):
                raise Exception("All detector configs must be a DetectorConfig instance")

        if not isinstance(common_simulation_config, SimulationCommonConfig):
            raise Exception("Common Simulation Config must be SimulationCommonConfig instance")
        
        for sim_config in simulation_configs:
            if not isinstance(sim_config, SimulationConfig):
                
                raise Exception("All simulation configs must be a SimulationConfig Instance")


        self.name = benchmark_name
        #Sets default configuration settings
        self.config = {
            NAME_KEY: benchmark_name,
            REPO_BRANCH_KEY: repo_branch,
            DETECTOR_CONFIG_KEY: [d_config.get_config() for d_config in detector_configs],
            SIMULATION_CONFIG_KEY: {
                SIMULATION_COMMON_KEY : common_simulation_config.get_config(),
                SIMULATION_LIST_KEY: [s_config.get_config() for s_config in simulation_configs]
            }        
        }

    def add_detector_config(self, detector_config):

        if not isinstance(detector_config, DetectorConfig):
            print("Detector config must be built from package defined class")
            return
        self.config[DETECTOR_CONFIG_KEY].append(detector_config.get_config())

    def set_common_simulation_config(self, common_sim_config):
        if not isinstance(common_sim_config, SimulationCommonConfig):
            print("Common simulation config must be built from Package defined class")
            return
        self.config[SIMULATION_CONFIG_KEY][SIMULATION_COMMON_KEY] = common_sim_config.get_config()
        
    def add_simulation_config(self, simulation_config):
        if not isinstance(simulation_config, SimulationConfig):
            print("Simulation config must be built from package defined class")
            return 
        self.config[SIMULATION_CONFIG_KEY][SIMULATION_LIST_KEY].append(simulation_config.get_config())

    def set_repository_branch(self, branch):
        if not isinstance(branch, str):
            print("Branch must be a string")
            return
        self.config[REPO_BRANCH_KEY] = branch

    def get_config(self):
        return self.config
        
    # def append_detector_set_config(self, detector_config_path, detector_name, module_component_name, attribute, new_value):

    #     return

    # def append_detector_add_config(self, detector_config_path, detector_name, module_component_name, new_attribute, new_value):

    #     return 
    
    # def append_detector_delete_config(self, detector_config_path, detector_name, module_component_name, attribute_to_remove):

    #     return 
    
    
    # def get_benchmark_dict(self, benchmark_name):
    #     for benchmark in self.get_all_benchmarks():
    #         if benchmark["name"] == benchmark_name:
    #             return benchmark
            
    #     print('Benchmark "{name}" not found'.format(name=benchmark_name))
    #     return {}
    
    # def get_detector_configs(self, benchmark_name):
        
    #     return self.config["detector_config"]
    
    # def get_simulation_common_config(self):
    #     return self.config["simulation_config"]["common"]
    
    # def get_simulation_list(self):
    #     return self.config["simulation_config"]["common"]
    
    # def get_simulation(self, benchmark_name, simulation_name):
    #     simulations = self.get_simulation_list(benchmark_name)
    #     for sim in simulations:
    #         if sim["simulation_name"] == simulation_name:
    #             return sim
    #     print('Simulation "{sim_name}" not found'.format(sim_name=simulation_name))

    # def set_branch(self, branch):

    #     self.config[""]


class BenchmarkSuiteConfig:

    def __init__(self, name="BenchmarkSuite", config_dir=CWD, autosave="false"):

        self.config = {
            BENCHMARK_SUITE_NAME_KEY: name,
            BENCHMARK_LIST_KEY: []
        }
        self.name = name
        self.dir_path = config_dir
        self.autosave=autosave
        if (self.autosave):
            self.save()

    def add_benchmark(self, benchmark):

        if not isinstance(benchmark, BenchmarkConfig):
            print("benchmark must have type: BenchmarkConfig")
            return
        self.config[BENCHMARK_LIST_KEY].append(benchmark.get_config())
        if self.autosave:
            self.save()

    def save(self):

        filename = "{name}_config.yml".format(name=self.name)
        dirpath = os.path.join(self.dir_path, filename)
        with open(dirpath, "w") as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)

    def reset_config(self):

        filename = "{name}_config.yml".format(name=self.name)
        dirpath = os.path.join(self.dir_path, filename)
        with open(dirpath, "w") as f:
            yaml.safe_dump({}, f, default_flow_style=False)
        
        