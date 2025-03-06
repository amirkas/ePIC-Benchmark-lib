import os
from pathlib import Path
from typing import Literal
from ePIC_benchmarks.simulation import SimulationConfig
from ePIC_benchmarks.detector import DetectorConfig
from ePIC_benchmarks.simulation.simulation_types import GunDistribution, Particle
from ePIC_benchmarks.benchmark import BenchmarkConfig
from ePIC_benchmarks.parsl.config import ParslConfig
from ePIC_benchmarks.parsl.executors import HighThroughputExecutorConfig, ThreadPoolExecutorConfig
from ePIC_benchmarks.parsl.providers import SlurmProviderConfig, LocalProviderConfig
from ePIC_benchmarks.parsl.launchers import SrunLauncherConfig
from ePIC_benchmarks.workflow import WorkflowConfig, run_from_file_path, run_from_config

#Generates eta bins with uniform intervals (step)
def generate_eta_ranges(min, max, step):

    ranges = []
    curr_min = min
    while curr_min <= max - step:

        curr_range = (curr_min, curr_min + step)
        ranges.append(curr_range)
        curr_min += step
    return ranges

################################
### Simulation Configuration ###
################################

#Number of npsim / eicrecon events to execute
NUM_EVENTS = 2000

#Location of the detector description xml file built after compilation
#This location is relative to ePIC/install/share/epic
DETECTOR_XML = "epic_craterlake_tracking_only.xml"

#Phase space used for npsim simulations
DISTRIBUTION = GunDistribution.Eta

#Particle used for npsim simulations
SIM_PARTICLE = Particle.PionPlus

#List of momenta in GeV
MOMENTUM = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20]

#List of Eta bins 
ETA_RANGES = generate_eta_ranges(-3, -1, 2)



##############################
### Detector Configuration ###
##############################

#List of distances for 'TrackerEndcapNDisk4_zmin' in cm
END_CAP_DISTANCES = [100] 

#Detector description xml file to change (path is relative to ePIC/compact)
CONFIGURE_DETECTOR_XML = "tracking/definitions_craterlake.xml"

#Value of the 'name' attribute of a <constant> XML element to lookup
CONFIGURE_DETECTOR_ATTRIBUTE = "TrackerEndcapNDisk4_zmin"


WORKFLOW_CONFIG_FILENAME = "workflow_config.yml"
WORKFLOW_SCRIPT_NAME = "workflow_script.py"

###############################
### Benchmark Configuration ###
###############################

#Branch of the ePIC repository to checkout
BRANCH = "25.02.0"

#Prefix for a benchmark's name. Each Benchmark must have a unique name. 
BENCHMARK_NAME_PREFIX = "Benchmark"

#Path to the current working directory
CWD = Path(os.getcwd())

##############################
### Workflow Configuration ###
##############################

#Name for the entire workflow
WORKFLOW_NAME = "Workflow"

#Option to keep the ePIC repository for each benchmark after workflow execution is complete
KEEP_EPIC = True

#Option to keep npsim outputs for each benchmark after workflow execution is complete
KEEP_NPSIM_OUTPUTS = True

#Option to keep the eicrecon outputs for each benchmark after workflow execution is complete
KEEP_EICRECON_OUTPUTS = True

#Name of the YAML configuration file to save to disk 
WORKFLOW_CONFIG_FILENAME = "workflow_config.yml"

#Name of the workflow script that defines tasks to run and the task depedency graph
WORKFLOW_SCRIPT_NAME = "workflow_script.py"

#Path for the YAML configuration file
WORKFLOW_CONFIG_FILEPATH = CWD.joinpath(WORKFLOW_CONFIG_FILENAME)

#Path for the workflow script python file
WORKFLOW_SCRIPT_PATH = CWD.joinpath(WORKFLOW_SCRIPT_NAME)

###########################
### Parsl Configuration ###
###########################

#Maximum amount of time alloted to run workflow on compute node (hours, minutes, seconds)
WALLTIME = "00:30:00"

#Number of tasks to execute concurrently (maximum of 128 * number of nodes)
NUM_CONCURRENT_TASKS = 32


#Formats endcap distances for correct updates to the detector description xml file.
def format_endcap_distances(endcap_distances):

    formatted = []
    for distance in endcap_distances:
        formatted.append(f'{distance}*cm')

    return formatted

#Generates detector configs from list of end_cap values. 
def generate_detector_configs(detector_file, lookup_attribute_name, lookup_attribute_value, edit_attribute_name, edit_attribute_values):

    all_detector_configs = []
    for edit_value in edit_attribute_values:

        detector_config = DetectorConfig(
            file=detector_file,
            constant_attributes={lookup_attribute_name : lookup_attribute_value},
            update_attribute=edit_attribute_name,
            update_value=edit_value,
            edit_type="SET"            
        )
        all_detector_configs.append(detector_config)

    return all_detector_configs


#Generates simulation configs from list of momenta and list of eta bins
#Note: If you do not want to generate/use a material map, either delete 'use_material_map=True' or set it to false
def generate_simulation_configs():

    sim_configs = []
    for momentum_value in MOMENTUM:
        for eta_bin in ETA_RANGES:
            new_config = SimulationConfig(
                eta_min=eta_bin[0],
                eta_max=eta_bin[1],
                num_events=NUM_EVENTS,
                momentum=momentum_value,
                distribution_type=DISTRIBUTION,
                particle=SIM_PARTICLE,
                detector_xml=DETECTOR_XML,
                use_material_map=True
            )
            sim_configs.append(new_config)

    return sim_configs

#Generates benchmark configs from list of detector_configs.
def generate_benchmark_configs():

    formatted_end_cap_distances = format_endcap_distances(END_CAP_DISTANCES)
    detector_configs = generate_detector_configs(CONFIGURE_DETECTOR_XML, "name", CONFIGURE_DETECTOR_ATTRIBUTE, "value", formatted_end_cap_distances)

    simulation_configs = generate_simulation_configs()
    benchmark_configs = []
    for distance, detector_config in zip(END_CAP_DISTANCES, detector_configs):

        benchmark_name = f"{BENCHMARK_NAME_PREFIX}_{distance}"
        benchmark_config = BenchmarkConfig(
            name=benchmark_name,
            epic_branch=BRANCH,
            simulation_configs=simulation_configs,
            detector_configs=[detector_config]
        )
        benchmark_configs.append(benchmark_config)

    return benchmark_configs

#Generates a parsl config that runs tasks locally on a compute node 
def generate_parsl_config(num_concurrent_tasks=32, walltime = "00:30:00"):

    cores_per_task = 128 / num_concurrent_tasks

    parsl_config = ParslConfig(
    executors=[
        HighThroughputExecutorConfig(
            label="Headless_Executor",
            cores_per_worker=cores_per_task,
            max_workers_per_node=num_concurrent_tasks,
            provider=LocalProviderConfig(
                nodes_per_block = 1,
                launcher=SrunLauncherConfig(overrides=f'-c {int(cores_per_task)}'),
                max_blocks=1,
                init_blocks=1,
            ),
        ),
        ]
    )
    return parsl_config

def generate_workflow_config():

    benchmark_configs = generate_benchmark_configs()
    workflow_config = WorkflowConfig(
        name=WORKFLOW_NAME,
        benchmarks=benchmark_configs,
        parsl_config=generate_parsl_config(num_concurrent_tasks=NUM_CONCURRENT_TASKS, walltime=WALLTIME),
        keep_epic_repos=KEEP_EPIC,
        keep_simulation_outputs=KEEP_NPSIM_OUTPUTS,
        keep_reconstruction_outputs=KEEP_EICRECON_OUTPUTS,
        redo_all_benchmarks=True,
        debug=True
    )
    return workflow_config

#Generate the workflow
workflow = generate_workflow_config()

#Save workflow to disk
workflow.save(WORKFLOW_CONFIG_FILEPATH)

#Run the workflow with a given script path
run_from_config(workflow, script_path=WORKFLOW_SCRIPT_PATH)


