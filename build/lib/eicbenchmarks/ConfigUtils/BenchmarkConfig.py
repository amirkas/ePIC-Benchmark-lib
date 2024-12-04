
from .SimulationConfig import SimulationConfig, SimulationCommonConfig, SIMULATION_NAME_KEY
from .DetectorConfig import DetectorConfig

DEFAULT_BRANCH = "main"

NAME_KEY = "name"
REPO_BRANCH_KEY = "repository_branch"
DETECTOR_CONFIG_KEY = "detector_config"
SIMULATION_CONFIG_KEY = "simulation_config"
SIMULATION_COMMON_KEY = "common"
SIMULATION_LIST_KEY = "simulations"

BENCHMARK_KEYS = [
    NAME_KEY, 
    REPO_BRANCH_KEY,
    DETECTOR_CONFIG_KEY,
    SIMULATION_COMMON_KEY,
    SIMULATION_LIST_KEY
]

class BenchmarkConfig:

    def __init__(self, load_benchmark_config=None, benchmark_name="benchmark", repo_branch=DEFAULT_BRANCH, detector_configs=[], common_simulation_config=SimulationCommonConfig(), simulation_configs=[]):

        if load_benchmark_config != None:
            if not isinstance(load_benchmark_config, dict):
                raise Exception("benchmark config to be loaded must be a python dictionary")
            for key, value in load_benchmark_config.items():
                if key in BENCHMARK_KEYS:
                    data = value
                    if key == DETECTOR_CONFIG_KEY:
                        to_set = []
                        for detector_dict in data:
                            to_set.append(DetectorConfig(load_config_dict=detector_dict))
                    if key == SIMULATION_COMMON_KEY:
                        to_set = SimulationConfig(load_simulation_config=data)
                    if key == SIMULATION_LIST_KEY:
                        to_set = []
                        for sim_dict in data:
                            to_set.append(SimulationConfig(load_simulation_config=sim_dict))
                    if key == NAME_KEY or key == REPO_BRANCH_KEY:
                        to_set = data
                    setattr(self, key, to_set)
            
            #TODO: Add load validation
        
        #Check if input objects have the correct type:
        for detector_config in detector_configs:
            if not isinstance(detector_config, DetectorConfig):
                raise Exception("All detector configs must be a DetectorConfig instance")

        if not isinstance(common_simulation_config, SimulationCommonConfig):
            raise Exception("Common Simulation Config must be SimulationCommonConfig instance")
        
        for sim_config in simulation_configs:
            if not isinstance(sim_config, SimulationConfig):
                
                raise Exception("All simulation configs must be a SimulationConfig Instance")

        setattr(self, NAME_KEY, benchmark_name)
        setattr(self, REPO_BRANCH_KEY, repo_branch)
        setattr(self, DETECTOR_CONFIG_KEY, detector_configs)
        setattr(self, SIMULATION_COMMON_KEY, common_simulation_config)
        setattr(self, SIMULATION_LIST_KEY, simulation_configs)
       

    def add_detector_config(self, detector_config):

        if not isinstance(detector_config, DetectorConfig):
            print("Detector config must be built from package defined class")
            return
        
        curr_list = getattr(self, DETECTOR_CONFIG_KEY)[:]
        curr_list.append(detector_config)
        setattr(self, DETECTOR_CONFIG_KEY, curr_list)

    def set_common_simulation_config(self, common_sim_config):
        if not isinstance(common_sim_config, SimulationCommonConfig):
            print("Common simulation config must be built from Package defined class")
            return
        setattr(self, SIMULATION_COMMON_KEY, common_sim_config)
        
    def add_simulation_config(self, simulation_config):
        if not isinstance(simulation_config, SimulationConfig):
            print("Simulation config must be built from package defined class")
            return 
        curr_list = getattr(self, SIMULATION_LIST_KEY)[:]
        curr_list.append(simulation_config)
        setattr(self, SIMULATION_LIST_KEY, curr_list)
        

    def set_repository_branch(self, branch):
        if not isinstance(branch, str):
            print("Branch must be a string")
            return
        setattr(self, REPO_BRANCH_KEY, branch)

    def get_config_dict(self):

        config = {}
        config[NAME_KEY] = getattr(self, NAME_KEY)
        config[REPO_BRANCH_KEY] = getattr(self, REPO_BRANCH_KEY)
        config[DETECTOR_CONFIG_KEY] = [detector_cfg.get_config_dict() for detector_cfg in getattr(self, DETECTOR_CONFIG_KEY)]
        config[SIMULATION_COMMON_KEY] = getattr(self, SIMULATION_COMMON_KEY).get_config_dict()
        config[SIMULATION_LIST_KEY] = [sim_cfg.get_config_dict() for sim_cfg in getattr(self, SIMULATION_LIST_KEY)]

        return config
    
    def get_branch(self):
        return getattr(self, REPO_BRANCH_KEY)
    
    def get_detector_configs(self):
        return getattr(self, DETECTOR_CONFIG_KEY)
    
    def get_common_simulation_config(self):
        return getattr(self, SIMULATION_COMMON_KEY)
    
    def get_simulation_config_list(self):
        return getattr(self, SIMULATION_LIST_KEY)
    
    def get_simulation_config(self, simulation_name : str):
        all_sims = self.get_simulation_config_list()
        for sim in all_sims:
            if simulation_name == getattr(sim, SIMULATION_NAME_KEY):
                return sim
            
        raise Exception("Could not find simulation with that name")
    
    def get_simulation_names(self):
        names = []
        all_sims = self.get_simulation_config_list()
        for sim in all_sims:
            names.append(getattr(sim, SIMULATION_NAME_KEY))
        return names



        