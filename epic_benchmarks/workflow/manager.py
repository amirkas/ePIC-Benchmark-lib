import os
import shutil
import re
import copy
from epic_benchmarks.configurations.benchmark_suite_config import BenchmarkSuiteConfig

BENCHMARK_DIR_NAME = "Benchmarks"
EPIC_DIR_NAME = "epic"
EPIC_COMPACT_NAME = "compact"
OUTPUT_DIR_NAME = "out"
SIMULATION_OUTPUT_NAME = "simulated"
RECONSTRUCTION_OUTPUT_NAME = "reconstructed"
ANALYSIS_OUTPUT_NAME = "analysis"

NPSIM_ENVIRONMENT_NAME = "npsim_temp"
EICRECON_ENVIRONMENT_NAME = "eicrecon_temp"

SIMULATION_FILE_PREFIX = "sim"
RECONSTRUCTION_FILE_PREFIX = "recon"
ANALYSIS_FILE_PREFIX= "resol_recon"
ANALYSIS_COMPLETE_PREFIX = "analysis_task"


ROOT_FILE_EXT = "root"
ANALYSIS_FILE_EXT = "png"
ANALYSIS_COMPLETE_FILE_EXT = ".txt"

SHIFTER_IMG = "eicweb/jug_xl:24.10.1-stable"
SHIFTER_ENTRY = "/opt/local/bin/eic-shell"

INSTALL_BASH_SCRIPT_REL_PATH = os.path.join("install", "bin", "thisepic.sh")
BUILD_DETECTOR_REL_PATH = os.path.join("install", "share", "epic")

def root_file_corrupted(rootfile_path):
    import uproot as up
    try:
        with up.open(rootfile_path) as f:
            keys = f.keys()
            if len(keys) == 0:
                return True
            f["events"]
            return False
    except:
        return True

#Helper Data Structure for organzing incomplete benchmark tasks
class _IncompleteBenchmarks:

    def __init__(self):
        self.incomplete = {}

    def add_npsim(self, benchmark_name, simulation_name):
        self._add_benchmark(benchmark_name)
        self.incomplete[benchmark_name]["npsim"].add(simulation_name)
        self.add_eicrecon(benchmark_name, simulation_name)

    def add_eicrecon(self, benchmark_name, simulation_name):
        self._add_benchmark(benchmark_name)
        self.incomplete[benchmark_name]["eicrecon"].add(simulation_name)
        self.add_analysis(benchmark_name, simulation_name)

    def add_analysis(self, benchmark_name, simulation_name):
        self._add_benchmark(benchmark_name)
        self.incomplete[benchmark_name]["analysis"].add(simulation_name)

    def get_incomplete_benchmarks(self):
        return self.incomplete.keys()

    def get_incomplete_npsims(self, benchmark_name):
        if benchmark_name not in self.incomplete.keys():
            print("Benchmark : {bc_name} is not incomplete".format(bc_name=benchmark_name))
        else:
            return self.incomplete[benchmark_name]["npsim"]

    def get_incomplete_eicrecons(self, benchmark_name):
        if benchmark_name not in self.incomplete.keys():
            print("Benchmark : {bc_name} is not incomplete".format(bc_name=benchmark_name))
        else:
            return self.incomplete[benchmark_name]["eicrecon"]

    def get_incomplete_analyses(self, benchmark_name):
        if benchmark_name not in self.incomplete.keys():
            print("Benchmark : {bc_name} is not incomplete".format(bc_name=benchmark_name))
        else:
            return self.incomplete[benchmark_name]["analysis"]
        
    def __repr__(self):
        incomplete_str = ""
        for benchmark_name in self.incomplete.keys():
            
            npsim_list = self.get_incomplete_npsims(benchmark_name)
            eicrecon_list = self.get_incomplete_eicrecons(benchmark_name)
            analysis_list = self.get_incomplete_analyses(benchmark_name)
            benchmark_name_str = "Benchmark to complete: {bc_name}".format(bc_name=benchmark_name)
            npsims_str = "npsim's to complete: {sims}".format(sims=" ".join(npsim_list))
            eicrecons_str = "eicrecons's to complete: {recons}".format(recons=" ".join(eicrecon_list))
            analyses_str = "analyses to complete: {analyses}".format(analyses=" ".join(analysis_list))
            curr_incomplete_str = f"{benchmark_name_str}\n    {npsims_str}\n    {eicrecons_str}\n    {analyses_str}\n"
            incomplete_str += curr_incomplete_str
        return incomplete_str

    def _add_benchmark(self, benchmark_name):
        if benchmark_name not in self.incomplete.keys():
            self.incomplete[benchmark_name] = {
                "npsim" : set(),
                "eicrecon" : set(),
                "analysis" : set()
            }



#Manager class for internal use that:
#   - Manages the workflow filsystem including initialization, workflow status, and cleanup
#   - Provides accessors for the workflow filesystem
#   - Provides accessors for the workflow configuration
#   - Provides generators for generic bash commands

class ParslWorkflowManager:


    def __init__(self, benchmark_suite, workdir, directory_name="Benchmarks", container_img_name=None, container_entry_cmd="", backup_benchmarks=True, output_pipes=[]):
        self.benchmark_suite = benchmark_suite
        self.benchmark_suite_name = self.benchmark_suite.get_benchmark_suite_name()
        self.workdir = workdir
        self.dir_name = directory_name
        self.suite_dir_path = os.path.join(self.workdir, self.dir_name)
        self.container_img = container_img_name
        self.container_entry_cmd = container_entry_cmd
        self.is_backup = False

        self.output_pipe_managers = []
        if len(output_pipes) != 0:
            for pipe_path in output_pipes:
                self.add_output_pipe(pipe_path)

    #Workflow filesystem managers

    def overwrite_benchmark(self):
        if self.is_backup:
            raise Exception("Cannot delete backup directories")
        CWD = os.getcwd()
        suite_dir = self.benchmark_suite_dir_path()
        if CWD == suite_dir:
            raise Exception("Cannot delete Current Working Directory")
        elif os.path.exists(suite_dir):
            shutil.rmtree(suite_dir, ignore_errors=True)

    def overwrite_all_simulation_outputs(self):
        if self.is_backup:
            raise Exception("Cannot delete backup directories")
        CWD = os.getcwd()
        for benchmark_name in self.get_benchmark_names():
            sim_output_dir = self.simulation_output_dir_path(benchmark_name)
            if CWD == sim_output_dir:
                raise Exception("Simulation output directory is the Current Working Directory -> Cannot Delete the Current Working Directory")
            else:
                shutil.rmtree(sim_output_dir, ignore_errors=True)
        
    def overwrite_all_reconstruction_outputs(self):
        if self.is_backup:
            raise Exception("Cannot delete backup directories")
        CWD = os.getcwd()
        for benchmark_name in self.get_benchmark_names():
            recon_output_dir = self.reconstruction_output_dir_path(benchmark_name)
            if CWD == recon_output_dir:
                raise Exception("Reconstruction output directory is the Current Working Directory -> Cannot Delete the Current Working Directory")
            else:
                shutil.rmtree(recon_output_dir, ignore_errors=True)
    
    def overwrite_all_analysis_outputs(self):
        if self.is_backup:
            raise Exception("Cannot delete backup directories")
        CWD = os.getcwd()
        for benchmark_name in self.get_benchmark_names():
            analysis_output_dir = self.analysis_output_dir_path(benchmark_name)
            if CWD == analysis_output_dir:
                raise Exception("analysis output directory is the Current Working Directory -> Cannot Delete the Current Working Directory")
            else:
                shutil.rmtree(analysis_output_dir, ignore_errors=True)

    def copy_benchmark_suite_content(self, new_directory_path):

        shutil.copytree(self.benchmark_suite_dir_path(), new_directory_path)

    def create_backup(self):

        #Find next backup number to use
        pattern = f'{self.dir_name}_Backup_(\d+)'
        directories_list = os.listdir(self.workdir)
        last_backup = -1
        for dir in directories_list:
            backup_match = re.match(pattern, dir)
            if backup_match:
                backup_num = int(backup_match.group(1))
                last_backup = max(last_backup, backup_num)
        new_backup_num = last_backup + 1
        new_dir_name = f'{self.dir_name}_Backup_{new_backup_num}'
        new_dir_path = os.path.join(self.workdir, new_dir_name)

        #Copy all content of Benchmark suite to the new backup directory
        self.copy_benchmark_suite_content(new_dir_path)
        #Copy benchmark suite configuration to the new backup directory for easy loading.
        suite_copy = copy.deepcopy(self.benchmark_suite)
        suite_copy.file_path = os.path.join(new_dir_path, "backup_config.yml")
        suite_copy.save()
    
    def load_backup(self, backup_number):

        pattern = f'{self.dir_name}_Backup_{backup_number}'
        directories_list = os.listdir(self.workdir)
        backup_dir_name = None
        for dir in directories_list:
            if re.match(pattern, dir):
                backup_dir_name = dir
                break
        if backup_dir_name == None:
            raise Exception(f"Could not find a backup for backup number: {backup_number}")
        
        backup_dir = os.path.join(self.workdir, backup_dir_name)
        suite_filepath = os.path.join(backup_dir, "backup_config.yml")
        new_suite_instance = BenchmarkSuiteConfig(suite_filepath)
        self.benchmark_suite = new_suite_instance
        self.dir_name = backup_dir_name
        self.suite_dir_path = backup_dir
        self.is_backup = True

    def initialize_directories(self, overwrite : bool, ignore_environment_dirs=False):

        if overwrite:
            self.overwrite_benchmark()
        
        self.init_directory(self.benchmark_suite_dir_path())
        benchmark_names = self.get_benchmark_names()
        for benchmark_name in benchmark_names:
            self.init_directory(self.benchmark_dir_path(benchmark_name))
            self.init_directory(self.simulation_output_dir_path(benchmark_name))
            self.init_directory(self.reconstruction_output_dir_path(benchmark_name))
            self.init_directory(self.analysis_output_dir_path(benchmark_name))
            simulation_names = self.get_simulation_names(benchmark_name)
            if not ignore_environment_dirs:
                for simulation_name in simulation_names:
                    self.init_directory(self.simulation_environment_dir_path(benchmark_name, simulation_name))
                    self.init_directory(self.reconstruction_environment_dir_path(benchmark_name, simulation_name))

    #Initialize another workflow manager instance with the output_path as its working directory. 
    def add_output_pipe(self, output_path, override_pipe_paths=True):

        pipe_manager = ParslWorkflowManager(self.benchmark_suite, output_path, "", None)
        pipe_manager.initialize_directories(overwrite=override_pipe_paths, ignore_environment_dirs=True)
        self.output_pipe_managers.append(pipe_manager)        

    def copy_to_output_pipes(self, benchmark_name, simulation_name):

        for pipe_manager in self.output_pipe_managers:
            shutil.copy2(self.simulation_output_file_path(benchmark_name, simulation_name), pipe_manager.simulation_output_file_path(benchmark_name, simulation_name))
            shutil.copy2(self.reconstruction_output_file_path(benchmark_name, simulation_name), pipe_manager.reconstruction_output_file_path(benchmark_name, simulation_name))

    def cleanup_workflow(self):

        incomplete_tasks = self.get_incomplete_tasks()
        if len(incomplete_tasks.get_incomplete_benchmarks()) != 0:
            print("Tasks that need still need to be completed:")
            print(incomplete_tasks)

        self.cleanup_directories()
        

    def cleanup_directories(self):
    
        benchmark_names = self.get_benchmark_names()
        for benchmark_name in benchmark_names:
            npsim_env_path = self.npsim_environment_dir_path(benchmark_name)
            eicrecon_env_path = self.eicrecon_environment_dir_path(benchmark_name)
            shutil.rmtree(npsim_env_path, ignore_errors=True)
            shutil.rmtree(eicrecon_env_path, ignore_errors=True)


    #Task completion analyzers

    def get_incomplete_tasks(self):

        incomplete_tasks = _IncompleteBenchmarks()

        benchmark_names = self.get_benchmark_names()
        for benchmark_name in benchmark_names:
            simulation_names = self.get_simulation_names(benchmark_name)
            for simulation_name in simulation_names:
                simulation_output_exists = self.simulation_output_file_exists(benchmark_name, simulation_name)
                reconstruction_output_exists = self.reconstruction_output_file_exists(benchmark_name, simulation_name)
                analysis_complete_exists = self.analysis_complete_file_exists(benchmark_name, simulation_name)

                if not simulation_output_exists or self.simulation_output_file_corrupted(benchmark_name, simulation_name):
                    incomplete_tasks.add_npsim(benchmark_name, simulation_name)

                elif not reconstruction_output_exists or self.reconstruction_output_file_corrupted(benchmark_name, simulation_name):
                    incomplete_tasks.add_eicrecon(benchmark_name, simulation_name)

                elif not analysis_complete_exists:
                    incomplete_tasks.add_analysis(benchmark_name, simulation_name)
        return incomplete_tasks

    #Configurtion Appliers
    def apply_detector_configs(self, benchmark_name):
        detector_configs = self.get_detector_config_list(benchmark_name)
        for detector_config in detector_configs:
            detector_config.apply_update(self.detector_description_dir_path(benchmark_name))


    #Configuration Accessors

    def get_benchmark_names(self):
        return self.benchmark_suite.get_benchmark_names()
    
    def get_simulation_names(self, benchmark_name):
        if benchmark_name not in self.get_benchmark_names():
            raise Exception(f"Benchmark with name '{benchmark_name}' does not exist")
        else:
            return self.benchmark_suite.get_simulation_names(benchmark_name)
        
    def get_benchmark_epic_branch(self, benchmark_name):
        return self.benchmark_suite.get_benchmark_branch(benchmark_name)
        
    def get_detector_config_list(self, benchmark_name):

        return self.benchmark_suite.get_benchmark_detector_configs(benchmark_name)

    def get_common_simulation_config(self, benchmark_name):

        return self.benchmark_suite.get_benchmark_common_sim(benchmark_name)
    
    def get_simulation_config(self, benchmark_name, simulation_name):

        return self.benchmark_suite.get_benchmark_simulation(benchmark_name, simulation_name)
    
    def has_container(self):
        return self.container_img != None and len(self.container_img) > 0

    #Directory and file path accessors

    def benchmark_suite_dir_path(self):
        return self.suite_dir_path
    
    def benchmark_dir_path(self, benchmark_name):

        return os.path.join(self.benchmark_suite_dir_path(), benchmark_name)
    
    def epic_dir_path(self, benchmark_name):

        return os.path.join(self.benchmark_dir_path(benchmark_name), EPIC_DIR_NAME)
    
    def detector_description_dir_path(self, benchmark_name, compact_dir=None):
        if compact_dir == None or len(compact_dir) == 0:
            return os.path.join(self.epic_dir_path(benchmark_name), EPIC_COMPACT_NAME)
        else:
            return os.path.join(self.epic_dir_path(benchmark_name), EPIC_COMPACT_NAME, compact_dir)
        
    def detector_description_file_path(self, benchmark_name, detector_filename, compact_dir=None):

        return os.path.join(self.detector_description_dir_path(benchmark_name, compact_dir), detector_filename)
    
    def detector_build_path(self, benchmark_name, share_dir=None):
        if share_dir == None or len(share_dir) == 0:
            return os.path.join(self.epic_dir_path(benchmark_name), BUILD_DETECTOR_REL_PATH)
        else:
            return os.path.join(self.epic_dir_path(benchmark_name), BUILD_DETECTOR_REL_PATH, share_dir)

    def output_dir_path(self, benchmark_name):

        return os.path.join(self.benchmark_dir_path(benchmark_name), OUTPUT_DIR_NAME)
    
    def simulation_output_dir_path(self, benchmark_name):

        return os.path.join(self.output_dir_path(benchmark_name), SIMULATION_OUTPUT_NAME)
    
    def reconstruction_output_dir_path(self, benchmark_name):

        return os.path.join(self.output_dir_path(benchmark_name), RECONSTRUCTION_OUTPUT_NAME)
    
    def analysis_output_dir_path(self, benchmark_name):

        return os.path.join(self.output_dir_path(benchmark_name), ANALYSIS_OUTPUT_NAME)
    
    def simulation_output_file_path(self, benchmark_name, simulation_name):

        filename = "{prefix}_{sim_name}.{ext}".format(prefix=SIMULATION_FILE_PREFIX, sim_name=simulation_name, ext=ROOT_FILE_EXT)
        return os.path.join(self.simulation_output_dir_path(benchmark_name), filename)
    
    def reconstruction_output_file_path(self, benchmark_name, simulation_name):

        filename = "{prefix}_{sim_name}.{ext}".format(prefix=RECONSTRUCTION_FILE_PREFIX, sim_name=simulation_name, ext=ROOT_FILE_EXT)
        return os.path.join(self.reconstruction_output_dir_path(benchmark_name), filename)
    
    def analysis_output_file_path(self, benchmark_name, simulation_name):

        filename = "{prefix}_{sim_name}.{ext}".format(prefix=ANALYSIS_FILE_PREFIX, sim_name=simulation_name, ext=ROOT_FILE_EXT)
        return os.path.join(self.analysis_output_dir_path(benchmark_name), filename)
    
    def analysis_complete_file_path(self, benchmark_name, simulation_name):
        filename = "{prefix}_{sim_name}.{ext}".format(prefix=ANALYSIS_COMPLETE_PREFIX, sim_name=simulation_name, ext=ANALYSIS_COMPLETE_FILE_EXT)
        return os.path.join(self.analysis_output_dir_path(benchmark_name), filename)

    def npsim_environment_dir_path(self, benchmark_name):
        return os.path.join(self.benchmark_dir_path(benchmark_name), NPSIM_ENVIRONMENT_NAME)
    
    def eicrecon_environment_dir_path(self, benchmark_name):
        return os.path.join(self.benchmark_dir_path(benchmark_name), EICRECON_ENVIRONMENT_NAME)
    
    def simulation_environment_dir_path(self, benchmark_name, simulation_name):
        return os.path.join(self.npsim_environment_dir_path(benchmark_name), simulation_name)
    
    def reconstruction_environment_dir_path(self, benchmark_name, simulation_name):
        return os.path.join(self.eicrecon_environment_dir_path(benchmark_name), simulation_name)
    
    #Directory initializer
    def init_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)

    
    #Directory and file path verification

    def benchmark_suite_dir_exists(self):

        return os.path.exists(self.benchmark_suite_dir_path())
    
    def benchmark_dir_exists(self, benchmark_name):

        return os.path.exists(self.benchmark_dir_path(benchmark_name))
    
    def epic_dir_exists(self, benchmark_name):

        return os.path.exists(self.epic_dir_path(benchmark_name))
    
    def epic_install_script_path(self, benchmark_name):

        return os.path.join(self.epic_dir_path(benchmark_name), INSTALL_BASH_SCRIPT_REL_PATH)
    
    def output_dir_exists(self, benchmark_name):

        return os.path.exists(self.output_dir_path(benchmark_name))
    
    def simulation_output_dir_exists(self, benchmark_name):

        return os.path.exists(self.simulation_output_dir_path(benchmark_name))
    
    def reconstruction_output_dir_exists(self, benchmark_name):

        return os.path.exists(self.reconstruction_output_dir_path(benchmark_name))
    
    def analysis_output_dir_exists(self, benchmark_name):

        return os.path.exists(self.analysis_output_dir_path(benchmark_name))
    
    def simulation_output_file_exists(self, benchmark_name, simulation_name):

        return os.path.exists(self.simulation_output_file_path(benchmark_name, simulation_name))
    
    def reconstruction_output_file_exists(self, benchmark_name, simulation_name):

        return os.path.exists(self.reconstruction_output_file_path(benchmark_name, simulation_name))
    
    def analysis_complete_file_exists(self, benchmark_name, simulation_name):
        return os.path.exists(self.analysis_complete_file_path(benchmark_name, simulation_name))
    
    def simulation_output_file_corrupted(self, benchmark_name, simulation_name):
        
        return root_file_corrupted(self.simulation_output_file_path(benchmark_name, simulation_name))
    
    def reconstruction_output_file_corrupted(self, benchmark_name, simulation_name):
        
        return root_file_corrupted(self.reconstruction_output_file_path(benchmark_name, simulation_name))

    # Bash command generators

    def source_epic_str(self, benchmark_name):

        return f'source {self.epic_install_script_path(benchmark_name)}'
    
    def pull_shifter_cmd_str(self):
        return f"shifterimg pull {self.container_img}"

    def shifter_wrapper_str(self, commands : list):

        if self.container_img == None:
            raise Exception("Container for workflow not defined")
        container_cmds = " && ".join(commands)
        shifter_wrapped_cmd = f'shifter --image={self.container_img} {self.container_entry_cmd} "{container_cmds}"'
        return shifter_wrapped_cmd
    
    def concatenate_commands(self, commands : list):
        return " && ".join(commands)
    
    def change_directory_str(self, directory):
        return f'cd {directory}'