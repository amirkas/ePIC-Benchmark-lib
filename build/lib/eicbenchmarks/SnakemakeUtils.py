from _constants import *
from ConfigUtils.ConfigFileUtils import XmlEditor

def sim_cmds_to_flag(attribute, value):

    if attribute == SIMULATION_ENABLE_GUN_KEY:
        if value:
            return CONFIG_TO_SIM_CMD[SIMULATION_ENABLE_GUN_KEY]
        return ""
    else:
        cmd_template = CONFIG_TO_SIM_CMD[attribute]
        return '{cmd}"{arg}"'.format(cmd=cmd_template, arg=value)
   
def generate_sim_commands(common_config, sim_config):

    combined_config = dict(common_config.items() | sim_config.items())
    cmd_str = ""
    for k, v in combined_config.items():
        if k != SIMULATION_NAME_KEY:
            cmd_str += sim_cmds_to_flag(k, v) + " "
    return cmd_str

def generate_recon_commands(common_config, sim_config):

    combined_config = dict(common_config.items() | sim_config.items())
    cmd_str = ""
    cmd_str += "{cmd}{detector_path}".format(
        cmd=CONFIG_TO_RECON_CMD[SIMULATION_DETECTOR_KEY],
        detector_path=combined_config[SIMULATION_DETECTOR_KEY])
    cmd_str += " {cmd}{events}".format(
        cmd=CONFIG_TO_RECON_CMD[SIMULATION_NUM_EVENTS_KEY],
        events=combined_config[SIMULATION_NUM_EVENTS_KEY])
    return cmd_str

def edit_detector(benchmark_name, detector_config):

    detector_file = detector_config[DETECTOR_FILE_KEY]
    detector_path = get_detector_path(benchmark_name, detector_file)
    editor = XmlEditor(detector_path, autosave=True)
    xpath_query = ""
    if DETECTOR_NAME_KEY in detector_config.keys():
        detector_name = detector_config[DETECTOR_NAME_KEY]
        xpath_query += "//{tag}[{attr}={name}]".format(
            tag=XPATH_DETECTOR_TAG,
            attr=XPATH_DETECTOR_NAME_ATTR,
            name=detector_name
        )
    if DETECTOR_MODULE_KEY in detector_config.keys():
        module_name = detector_config[DETECTOR_MODULE_KEY]
        xpath_query += "//{tag}[{attr}={name}]".format(\
            tag=XPATH_MODULE_TAG,
            attr=XPATH_MODULE_NAME_ATTR,
            name=module_name
        )
    if DETECTOR_MODULE_COMPONENT_KEY in detector_config.keys():
        component_name = detector_config[DETECTOR_MODULE_COMPONENT_KEY]
        xpath_query += "//{tag}[{attr}={name}]".format(\
            tag=XPATH_COMPONENT_TAG,
            attr=XPATH_COMPONENT_NAME_ATTR,
            name=component_name
        )
    print(xpath_query)
    edit_type = detector_config[DETECTOR_TYPE_KEY]
    if edit_type == "set":
        edit_attribute = detector_config[DETECTOR_ATTRIBUTE_KEY]
        edit_value = detector_config[DETECTOR_VALUE_KEY]
        editor.set_attribute_xpath(xpath_query, edit_attribute, edit_value)

def edit_all_detectors(config, benchmark_name):

    detector_configs = get_benchmark_detector_configs(config, benchmark_name)
    for d_config in detector_configs:
        edit_detector(benchmark_name, d_config)

def get_benchmark(config, benchmark_name):

    return next((bc for bc in config[BENCHMARK_LIST_KEY] if bc[NAME_KEY] == benchmark_name), None)

def get_benchmark_branch(config, benchmark_name):

    bc = get_benchmark(config, benchmark_name)
    return bc[REPO_BRANCH_KEY]

def get_benchmark_detector_configs(config, benchmark_name):

    bc = get_benchmark(config, benchmark_name)
    return bc[DETECTOR_CONFIG_KEY]

def get_detector_path(benchmark_name, detector_file):
    return "benchmarks/{bc_name}/epic/compact/{detector}".format(bc_name=benchmark_name, detector=detector_file)


def get_benchmark_common_sim(config, benchmark_name):
    
    bc = get_benchmark(config, benchmark_name)
    return bc[SIMULATION_CONFIG_KEY][SIMULATION_COMMON_KEY]

def get_benchmark_simulation(config, benchmark_name, simulation_name):

    bc = get_benchmark(config, benchmark_name)
    return next((sim for sim in bc[SIMULATION_CONFIG_KEY][SIMULATION_LIST_KEY] if sim[SIMULATION_NAME_KEY] == simulation_name), None)

def get_benchmark_source_cmd(benchmark_name):

    return "source benchmarks/{bc_name}/epic/install/bin/thisepic.sh".format(bc_name=benchmark_name)