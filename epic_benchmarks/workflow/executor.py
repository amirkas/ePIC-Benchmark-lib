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

# def init_directories(benchmark_suite : BenchmarkSuiteConfig, workdir : str, overwrite):

#     benchmark_top_dir = fp.benchmark_suite_dir(workdir)
#     if os.path.exists(benchmark_top_dir) and overwrite:
#         if benchmark_top_dir == CWD:
#             raise Exception("Cannot delete Current Working Directory")
#         shutil.rmtree(benchmark_top_dir)

#     if overwrite:
#         benchmark_names = benchmark_suite.get_benchmark_names()
#         for benchmark_name in benchmark_names:
#             simulated_dir = fp.simulation_output_dir(benchmark_name=benchmark_name, workdir=workdir)
#             reconstructed_dir = fp.reconstruction_output_dir(benchmark_name=benchmark_name, workdir=workdir)
#             analysis_dir = fp.analysis_output_dir_path(benchmark_name=benchmark_name, workdir=workdir)
#             os.makedirs(simulated_dir, exist_ok=True)
#             os.makedirs(reconstructed_dir, exist_ok=True)
#             os.makedirs(analysis_dir)
#             for sim_name in benchmark_suite.get_simulation_names(benchmark_name):
#                 npsim_env_dir = fp.npsim_environment_dir(benchmark_name, workdir, sim_name)
#                 recon_env_dir = fp.eicrecon_environment_dir(benchmark_name, workdir, sim_name)
#                 os.makedirs(npsim_env_dir)
#                 os.makedirs(recon_env_dir)

# class incompleteBenchmarks:

#     def __init__(self):
#         self.incomplete = {}

#     def add_npsim(self, benchmark_name, simulation_name):
#         self._add_benchmark(benchmark_name)
#         self.incomplete[benchmark_name]["npsim"].add(simulation_name)
#         self.add_eicrecon(benchmark_name, simulation_name)

#     def add_eicrecon(self, benchmark_name, simulation_name):
#         self._add_benchmark(benchmark_name)
#         self.incomplete[benchmark_name]["eicrecon"].add(simulation_name)
#         self.add_analysis(benchmark_name, simulation_name)

#     def add_analysis(self, benchmark_name, simulation_name):
#         self._add_benchmark(benchmark_name)
#         self.incomplete[benchmark_name]["analysis"].add(simulation_name)

#     def get_incomplete_benchmarks(self):
#         return self.incomplete.keys()

#     def get_incomplete_npsim(self, benchmark_name):
#         if benchmark_name not in self.incomplete.keys():
#             print("Benchmark : {bc_name} is not incomplete".format(bc_name=benchmark_name))
#         else:
#             return self.incomplete[benchmark_name]["npsim"]

#     def get_incomplete_eicrecon(self, benchmark_name):
#         if benchmark_name not in self.incomplete.keys():
#             print("Benchmark : {bc_name} is not incomplete".format(bc_name=benchmark_name))
#         else:
#             return self.incomplete[benchmark_name]["eicrecon"]

#     def get_incomplete_analysis(self, benchmark_name):
#         if benchmark_name not in self.incomplete.keys():
#             print("Benchmark : {bc_name} is not incomplete".format(bc_name=benchmark_name))
#         else:
#             return self.incomplete[benchmark_name]["analysis"]

#     def __repr__(self):
#         incomplete_str = ""
#         for benchmark_name in self.incomplete.keys():
            
#             npsim_list = self.get_incomplete_npsim(benchmark_name)
#             eicrecon_list = self.get_incomplete_eicrecon(benchmark_name)
#             analysis_list = self.get_incomplete_analysis(benchmark_name)
#             benchmark_name_str = "Benchmark to complete: {bc_name}".format(bc_name=benchmark_name)
#             npsims_str = "npsim's to complete: {sims}".format(sims=" ".join(npsim_list))
#             eicrecons_str = "eicrecons's to complete: {recons}".format(recons=" ".join(eicrecon_list))
#             analyses_str = "analyses to complete: {analyses}".format(analyses=" ".join(analysis_list))
#             curr_incomplete_str = f"{benchmark_name_str}\n    {npsims_str}\n    {eicrecons_str}\n    {analyses_str}\n"
#             incomplete_str += curr_incomplete_str
#         return incomplete_str


#     def _add_benchmark(self, benchmark_name):
#         if benchmark_name not in self.incomplete.keys():
#             self.incomplete[benchmark_name] = {
#                     "npsim" : set(),
#                     "eicrecon" : set(),
#                     "analysis" : set()
#                 }



# def get_incomplete_tasks(benchmark_suite : BenchmarkSuiteConfig, workdir : str):

#     incomplete = incompleteBenchmarks()

#     benchmark_names = benchmark_suite.get_benchmark_names()
#     for benchmark_name in benchmark_names:
#         simulation_names = benchmark_suite.get_simulation_names(benchmark_name)
#         #Add task to incomplete tasks if output file for task doesn't exist or is corrupted (due to early termination or other causes)
#         for sim_name in simulation_names:
#             if not fp.simulation_output_exists(benchmark_name, workdir, sim_name) or fp.is_npsim_output_corrupted(benchmark_name, workdir, sim_name):
#                 incomplete.add_npsim(benchmark_name, sim_name)
#             if not fp.reconstruction_output_exists(benchmark_name, workdir, sim_name) or fp.is_eicrecon_output_corrupted(benchmark_name, workdir, sim_name):
#                 incomplete.add_eicrecon(benchmark_name, sim_name)
#             if not fp.analysis_output_exists(benchmark_name, workdir, sim_name):
#                 incomplete.add_analysis(benchmark_name, sim_name)
#     return incomplete
            


# def run_benchmarks(cores_per_node : int, cores_per_worker : int, num_nodes : int, charge_account=None, walltime_hours=None, walltime_mins=None, walltime_secs=0, qos="debug", use_slurm_provider=True, benchmark_suite_config=None, benchmark_config_file_path=None, workdir=CWD, complete_last_run=True, debug=False, overwrite=False):

#     if use_slurm_provider:
#         if charge_account == None:
#             raise Exception("Must provide charge group")
#         if walltime_hours == None and walltime_mins == None:
#             raise Exception("Must provide walltime")
#         parsl_config = SlurmProviderConfig(cores_per_node, cores_per_worker, num_nodes, charge_account, walltime_hours, walltime_mins, walltime_secs, qos)
#     else:
#         parsl_config = HeadlessConfig(cores_per_node, cores_per_worker, num_nodes)

#     benchmark_suite = load_config(workdir=workdir, benchmark_suite_config=benchmark_suite_config, benchmark_config_file_path=benchmark_config_file_path)
#     #Initialize directories if overwrite = True and complete_last_run = False
#     if not complete_last_run:
#         init_directories(benchmark_suite, workdir, overwrite)
#     parsl.load(parsl_config)
#     try:
#         if debug:
#             parsl.set_stream_logger(level=logging.DEBUG)
#             setup_logging()
        
#         all_futures = []
        
#         #If completing an incomplete run, define workflow based on unfinished tasks
#         if complete_last_run:
#             incomplete_tasks = get_incomplete_tasks(benchmark_suite, workdir)
#             benchmarks_to_run = incomplete_tasks.get_incomplete_benchmarks()
#             shifter_pull_future = pull_image(workdir)
#             for benchmark_name in benchmarks_to_run:
                
#                 #delete epic repository and re-clone it
#                 epic_repo = fp.epic_dir(benchmark_name, workdir)
#                 if os.path.exists(epic_repo):
#                     shutil.rmtree(epic_repo)

#                 clone_future = clone_epic(benchmark_name, workdir, shifter_pull_future)
                
#                 branch = benchmark_suite.get_benchmark_branch(benchmark_name)
#                 checkout_future = checkout_branch(benchmark_name, workdir, clone_future, branch=branch)
                
#                 detector_configs_future = load_detector_configs(benchmark_suite, benchmark_name, workdir, checkout_future)
                
#                 compile_future = compile_epic(benchmark_name, workdir, detector_configs_future)

#                 #Only run incomplete tasks (npsim, eicrecon, analysis)
#                 npsim_futures = {}
#                 for npsim_name in incomplete_tasks.get_incomplete_npsim(benchmark_name):
#                     sim_future = run_simulations(benchmark_suite, benchmark_name, npsim_name, workdir, compile_future)
#                     npsim_futures[npsim_name] = sim_future
                
#                 #Establish dependency on npsim task only if it was completed this run, otherwise dependency is on compile epic
#                 eicrecon_futures = {}
#                 for eicrecon_name in incomplete_tasks.get_incomplete_eicrecon(benchmark_name):
#                     if eicrecon_name in npsim_futures.keys():
#                         recon_future = run_reconstructions(benchmark_suite, benchmark_name, eicrecon_name, workdir, npsim_futures[eicrecon_name])
#                     else:
#                         recon_future = run_reconstructions(benchmark_suite, benchmark_name, eicrecon_name, workdir, compile_future)
#                     eicrecon_futures[eicrecon_name] = recon_future

#                 #Establish dependency on eicrecon task only if it was completed this run, otherwise dependency is on compile epic
#                 for analysis_name in incomplete_tasks.get_incomplete_analysis(benchmark_name):
#                     if analysis_name in eicrecon_futures.keys():
#                         analysis_future = save_performance_plot(benchmark_name, analysis_name, workdir, eicrecon_futures[analysis_name])
#                     else:
#                         analysis_future = save_performance_plot(benchmark_name, analysis_name, workdir, compile_future)
#                     all_futures.append(analysis_future)

#         #Else define workflow for fresh run
#         else:
#             benchmark_names = benchmark_suite.get_benchmark_names()
#             shifter_pull_future = pull_image(workdir)
#             for benchmark_name in benchmark_names:
                
#                 clone_future = clone_epic(benchmark_name, workdir, shifter_pull_future)
                
#                 branch = benchmark_suite.get_benchmark_branch(benchmark_name)
#                 checkout_future = checkout_branch(benchmark_name, workdir, clone_future, branch=branch)
                
#                 detector_configs_future = load_detector_configs(benchmark_suite, benchmark_name, workdir, checkout_future)
                
#                 compile_future = compile_epic(benchmark_name, workdir, detector_configs_future)

#                 simulation_names = benchmark_suite.get_simulation_names(benchmark_name)
#                 for simulation_name in simulation_names:
#                     sim_future = run_simulations(benchmark_suite, benchmark_name, simulation_name, workdir, compile_future)
                    
#                     recon_future = run_reconstructions(benchmark_suite, benchmark_name, simulation_name, workdir, sim_future)

#                     analysis_future = save_performance_plot(benchmark_name, simulation_name, workdir, recon_future)

#                     all_futures.append(analysis_future)

#         for fu in all_futures:
#             print(fu.result())
#             print(fu.stdout)
#     finally:

#         parsl.dfk().cleanup()


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


            







    

    

    
            

