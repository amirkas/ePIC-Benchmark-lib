import os
import shutil
import logging
import parsl
from dataclasses import dataclass, field
from parsl.config import Config
import re
from epic_benchmarks.configurations.benchmark_suite_config import BenchmarkSuiteConfig
from epic_benchmarks.workflow.repo_apps import pull_image, clone_epic, checkout_branch, load_detector_configs, compile_epic
from epic_benchmarks.workflow.simulation_apps import run_simulations, run_reconstructions
from epic_benchmarks.workflow.analysis_apps import save_performance_plot
from epic_benchmarks.workflow.parsl_configs import SlurmProviderConfig, HeadlessConfig, load_config
from epic_benchmarks.utils.time import convert_hours_to_seconds, convert_minutes_to_seconds, convert_seconds_to_time_tuple
from epic_benchmarks.workflow.manager import ParslWorkflowManager

CWD = os.getcwd()
DEFAULT_DIR = os.path.join(CWD, "Benchmarks")


def setup_logging():
    # Set up logging with detailed verbosity
    logger = logging.getLogger('parsl')
    logger.setLevel(logging.DEBUG)

    # StreamHandler to display logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Formatter to include timestamp, log level, and message
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    # FileHandler to log to a file (optional)
    file_handler = logging.FileHandler('parsl_debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

NoParslConfigError = AttributeError(
"""
Parsl Configuration must be provided upon initialize or set with any of the following methods:
    - set_headless_parsl_config
    - set_slurm_provider_config
""")

@dataclass
class WorkflowExecutor:

    name: str = "Workflow Executor"
    working_directory : str = os.getcwd()
    benchmark_directory_name : str = "Benchmarks"
    benchmark_suite_config: BenchmarkSuiteConfig = field(default=None)
    benchmark_suite_config_filename : str = field(default=None)
    container_img: str = None
    container_entry_command : str = ""
    debug: bool = True
    overwrite: bool = False
    backup_benchmarks = True
    workflow_manager: ParslWorkflowManager = None
    parsl_config: Config = None

    def __post_init__(self):
        if self.benchmark_suite_config == None and self.benchmark_suite_config_filename == None:
            raise Exception("You must provide either an instance of BenchmarkSuiteConfig or the filepath to a configuration file")
        if self.benchmark_suite_config == None:
            try:
                config_filepath = os.path.join(self.working_directory, self.benchmark_suite_config_filename)
                self.benchmark_suite_config = BenchmarkSuiteConfig(config_filepath)
            except:
                raise Exception("Invalid filepath or configuration")
        self.workflow_manager = ParslWorkflowManager(
            self.benchmark_suite_config,
            self.working_directory,
            directory_name=self.benchmark_directory_name,
            container_img_name=self.container_img,
            container_entry_cmd=self.container_entry_command,
            backup_benchmarks=self.backup_benchmarks
        )
        
    #Creates headless parsl config
    def set_headless_parsl_config(self, num_nodes : int, num_cores_per_node : int, num_cores_per_worker=1):
        pass

    def generate_headless_submit_script(self, num_nodes : int, cores_per_node : int, charge_account : str, *, walltime_str=None, walltime_hours=0, walltime_minutes=0, walltime_seconds=0, filename="submit_headless_workflow.sl"):
        pass
        if not filename.endswith(".sl"):
            print("Script not generated. Filename must end in .sl")

    
    def set_slurm_provider_config(self, num_nodes : int, cores_per_node : int, charge_account : str, cores_per_worker=1, qos='debug', walltime_str=None, walltime_hours=0, walltime_minutes=0, walltime_seconds=0):

        if walltime_str != None:
            time_pattern = '^(\d{2}):(\d{2}):(\d{2})$'
            match = re.match(time_pattern, walltime_str)
            if not match:
                raise ValueError(f"Invalid Walltime format: {walltime_str}.\nThe Walltime string, if defined, must use the format hh:mm:ss")
            hours = match.group(1)
            minutes = match.group(2)
            seconds = match.group(3)

        else:
            total_seconds = walltime_seconds + convert_minutes_to_seconds(walltime_minutes) + convert_hours_to_seconds(walltime_hours)
            hours, minutes, seconds = convert_seconds_to_time_tuple(total_seconds)

            if hours // 100 >= 1:
                raise Exception(f"""Cannot have a walltime for more than 100 hours.
                                Total input hours: {hours}
                                Total input minutes: {minutes}
                                Total input seconds: {seconds}"""
                                )
            
            worker_run_dir = f'{self.benchmark_directory_name}/runinfo'
        self.parsl_config = SlurmProviderConfig(num_nodes, cores_per_node, charge_account, walltime_hours=hours, walltime_mins=minutes, walltime_secs=seconds, QoS=qos, num_cores_per_worker=cores_per_worker, rundir=worker_run_dir)

        
    def run_benchmarks(self):

        if self.parsl_config == None:
            raise NoParslConfigError()
        
        #Initialize directories
        self.workflow_manager.initialize_directories(self.overwrite)

        #Find incomplete tasks based on previously ran workflows
        incomplete_tasks = self.workflow_manager.get_incomplete_tasks()
        incomplete_benchmark_names = incomplete_tasks.get_incomplete_benchmarks()

        #If no incomplete tasks exist, exit early
        if len(incomplete_benchmark_names) == 0:
            return
        
        print(incomplete_tasks)
        
        #Get maximum number of threads (cores) per worker
        nthreads = self.parsl_config.executors[0].cores_per_worker

        #Load parsl config
        parsl.load(self.parsl_config)

        try:
        
            #If debugging set to true, setup logging
            if self.debug:
                setup_logging()

            #Initialize list of final futures to wait for
            final_futures = []

            #Edge Case: If only analysis tasks need to be done, only complete those tasks without setting up
            #           the simulation enviornment. 
            if not incomplete_tasks.has_simulations():
                for benchmark_name in incomplete_benchmark_names:
                    analysis_names = incomplete_tasks.get_incomplete_analysis(benchmark_name)
                    for analysis_name in analysis_names:
                        analysis_future = save_performance_plot(self.workflow_manager, benchmark_name, analysis_name, None)
                        final_futures.append(analysis_future)

            else:
                #Pull shifter image if specified
                pull_container_future = None
                if self.workflow_manager.has_container():
                    pull_container_future = pull_image(self.workflow_manager)
                
                for benchmark_name in incomplete_benchmark_names:

                    #Delete epic repository if it exists for fresh repository
                    if self.workflow_manager.epic_dir_exists(benchmark_name):
                        epic_dir_path = self.workflow_manager.epic_dir_path(benchmark_name)
                        shutil.rmtree(epic_dir_path)

                    #Execute clone epic app
                    clone_future = clone_epic(benchmark_name, self.workflow_manager, pull_container_future)

                    #Execute checkout branch app
                    checkout_future = checkout_branch(benchmark_name, self.workflow_manager, clone_future)

                    detector_config_load_future = load_detector_configs(benchmark_name, self.workflow_manager, checkout_future)

                    #Execute compile epic app
                    compile_future = compile_epic(benchmark_name, self.workflow_manager, detector_config_load_future, nthreads)

                    incomplete_npsim_names = incomplete_tasks.get_incomplete_npsim(benchmark_name)
                    npsim_futures_map = {}
                    for npsim_name in incomplete_npsim_names:
                        npsim_future = run_simulations(self.workflow_manager, benchmark_name, npsim_name, compile_future)
                        npsim_futures_map[npsim_name] = npsim_future

                    incomplete_eicrecon_names = incomplete_tasks.get_incomplete_eicrecon(benchmark_name)
                    eicrecon_futures_map = {}
                    for eicrecon_name in incomplete_eicrecon_names:
                        if eicrecon_name in npsim_futures_map.keys():
                            eicrecon_dependence_future = npsim_futures_map[eicrecon_name]
                        else:
                            eicrecon_dependence_future = compile_future
                        eicrecon_future = run_reconstructions(self.workflow_manager, benchmark_name, eicrecon_name, eicrecon_dependence_future, nthreads)
                        eicrecon_futures_map[eicrecon_name] = eicrecon_future

                    incomplete_analysis_names = incomplete_tasks.get_incomplete_analysis(benchmark_name)
                    for analysis_name in incomplete_analysis_names:
                        if analysis_name in eicrecon_futures_map.keys():
                            analysis_dependence_future = eicrecon_futures_map[analysis_name]
                        else:
                            analysis_dependence_future = compile_future
                        analysis_future = save_performance_plot(self.workflow_manager, benchmark_name, analysis_name, analysis_dependence_future)
                        final_futures.append(analysis_future)
                
            for task_future in final_futures:
                print(task_future.result())

        #Cleanup workflow resources and directories
        finally:
            try:
                self.workflow_manager.cleanup_directories()
            finally:
                parsl.dfk().cleanup()


            







    

    

    
            

