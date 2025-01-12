import os
import shutil
import logging
from functools import cached_property, wraps
from pathlib import Path

from typing import Union, Optional, Self, List

import parsl
from dataclasses import dataclass, field

from parsl import bash_app, python_app
from parsl.config import Config
from parsl.configs.local_threads import config
from parsl.dataflow.futures import AppFuture
from parsl.utils import get_all_checkpoints
import re

from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from pydantic_core.core_schema import ValidationInfo, computed_field

from epic_benchmarks.configurations import BenchmarkSuiteConfig, BenchmarkSuiteConfig, SimulationConfig, \
    BenchmarkConfig
from epic_benchmarks.workflow.containers import ContainerCli, pull_image
# from epic_benchmarks.configurations.benchmark_suite_config import BenchmarkSuiteConfig
from epic_benchmarks.workflow.repo_apps import pull_image, clone_epic, checkout_branch, load_detector_configs, compile_epic
from epic_benchmarks.workflow.simulation_apps import run_simulations, run_reconstructions
from epic_benchmarks.workflow.analysis_apps import save_performance_plot
from epic_benchmarks.workflow.parsl_configs import SlurmProviderConfig, HeadlessConfig, load_config
from epic_benchmarks.utils.time import convert_hours_to_seconds, convert_minutes_to_seconds, convert_seconds_to_time_tuple
from epic_benchmarks.workflow.manager import ParslWorkflowManager
from epic_benchmarks.workflow import SUPPORTED_CONTAINERS, EPIC_REPO_URL

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


def containerize(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        container_cli = getattr(self, 'container_cli', None)
        standard_bash_cmd = func(*args, **kwargs)
        if container_cli:
            assert isinstance(container_cli, ContainerCli)
            return container_cli.commands_in_container(standard_bash_cmd)
        return standard_bash_cmd
    return wrapper

def containerized_bash_app(func):

    return bash_app(containerize(func))


def epic_benchmarks_bash_app():
    @bash_app
    def bash_app_wrapper(func):

        def container_wrapper(self, *args, **kwargs):
            container_cli = getattr(self, "container_cli", None)
            standard_bash_cmd = func(*args, **kwargs)
            if container_cli:
                return container_cli.commands_in_container(standard_bash_cmd)
            return standard_bash_cmd

        return container_wrapper
    return bash_app_wrapper

def concatenate_commands(*commands : List[str]):

    return ' && '.join(commands)


class BaseWorkflowExecutor(BaseModel):

    name : str = Field(default="Workflow Executor")
    working_directory : str = Field(default_factory=os.getcwd)
    benchmark_suite_config_filepath : Optional[str] = Field(default=None)
    benchmark_suite_config : Optional[BenchmarkSuiteConfig] = Field(default=None)
    container : Optional[str] = Field(default=None)
    container_image : Optional[str] = Field(default=None)
    container_entry_command : Optional[str] = Field(default=None)
    debug : bool = Field(default=False)
    redo_all_benchmarks : bool = Field(default=False)
    backup_benchmarks : bool = Field(default=True)
    parsl_config : Optional[Config] = Field(default=None)
    keep_epic_repos : bool = Field(default=False)
    keep_simulation_outputs : bool = Field(default=False)
    keep_reconstruction_outputs : bool = Field(default=False)

    @field_validator('benchmark_suite_config', mode='before')
    def validate_benchmark_suite_config(cls, value : Any, info : ValidationInfo) -> BenchmarkSuiteConfig:
        load_file_path = info.data["benchmark_suite_config_filepath"]
        if value is None:
            if load_file_path is None:
                raise ValueError("Must provide a benchmark suite config, or path to file path to load the config")
            bc_suite_config = BenchmarkSuiteConfig.load_from_file(load_file_path)
            return bc_suite_config
        elif value and load_file_path:
            raise ValueError("Cannot provide both a benchmark suite config, and path to load a config")
        elif isinstance(value, dict):
            return BenchmarkSuiteConfig(**value)
        elif isinstance(value, BenchmarkSuiteConfig):
            return value
        else:
            err = f"Benchmark suite could not be parsed"
            raise ValueError(err)

    @field_validator('parsl_config', mode='before')
    def validate_parsl_config(cls, value : Any, info : ValidationInfo) -> Config:
        if value is None:
            bc_suite_config = info.data["benchmark_suite_config"]
            assert isinstance(bc_suite_config, BenchmarkSuiteConfig)
            if bc_suite_config.parsl_config is None:
                raise ValueError("Must provide a Parsl Config if Benchmark suite config does not include one")
            return bc_suite_config.parsl_config.to_parsl_config_object()
        elif isinstance(value, dict):
            return Config(**value)
        elif isinstance(value, Config):
            return value
        else:
            raise ValueError("Could not parse parsl configuration")

    @model_validator(mode='after')
    def validate_container_info(self) -> Self:

        if self.container and self.container not in SUPPORTED_CONTAINERS:
            err = "Container must be one of {}".format(SUPPORTED_CONTAINERS)
            raise ValueError(err)
        if self.container_image and not self.container:
            err = "Must provide a container when providing a container image"
            raise ValueError(err)
        if self.container_entry_command and not self.container_image:
            err = "Must provide a container image when providing a container entry command"
            raise ValueError(err)
        return self

    @computed_field('container_cli', return_schema=Optional[ContainerCli])
    @cached_property
    def container_cli(self) -> Optional[ContainerCli]:

        if self.container:
            return ContainerCli(self.container, self.container_image, self.container_entry_command)
        return None

    def workflow(self, workflow_futures : List[AppFuture], container_pull_future : Optional[AppFuture]) -> None:

        raise NotImplementedError("Workflow must be implemented by derived class")

    def run_benchmarks(self):

        #Initialize any uninitialized directories
        self.init_directories()

        #Set checkpointing mode to checkpoint on task exit.
        config.checkpoint_mode = "task_exit"

        #If workflow is not being redone, start from the last recorded checkpoints
        if not self.redo_all_benchmarks:

            config.checkpoint_files = get_all_checkpoints()

        #Load Provided Parsl Config
        parsl.load(self.parsl_config)

        try:
            all_futures = []
            #If container image is provided. Attempt to pull it
            container_pull_future = None
            if self.container_cli:
                container_pull_future = pull_image(self.container_cli)
                all_futures.append(container_pull_future)

            #Add workflow defined by derived class to task dependency graph
            self.workflow(all_futures, container_pull_future)

            #Wait for every task to complete
            for task_future in all_futures:
                assert(isinstance(task_future, AppFuture))
                task_future.result()

        except:
            #Ensure cleanup keeps all files regardless of config settings if workflow terminates early.
            #Guarantees checkpointing will work as intended.
            self.keep_epic_repos = True
            self.keep_simulation_outputs = True
            self.keep_reconstruction_outputs= True

        finally:
            #Cleanup routine
            try:
                self.cleanup_directories()
            finally:
                parsl.dfk().cleanup()


    def init_directories(self):

        for benchmark_name in self._benchmark_names():

            benchmark_dir_path = self._benchmark_dir_path(benchmark_name)
            benchmark_dir_path.mkdir(parents=True, exist_ok=True)

            epic_path = self._epic_repo_path(benchmark_name)
            epic_path.mkdir(parents=True, exist_ok=True)

            sim_out_dir_path = self._sim_out_dir_path(benchmark_name)
            sim_out_dir_path.mkdir(parents=True, exist_ok=True)

            recon_out_dir_path = self._recon_out_dir_path(benchmark_name)
            recon_out_dir_path.mkdir(parents=True, exist_ok=True)

            sim_temp_dir_path = self._sim_temp_dir_path(benchmark_name)
            sim_temp_dir_path.mkdir(parents=True, exist_ok=True)

            recon_temp_dir_path = self._recon_temp_dir_path(benchmark_name)
            recon_temp_dir_path.mkdir(parents=True, exist_ok=True)


    def cleanup_directories(self):

        for benchmark_name in self._benchmark_names():

            if not self.keep_epic_repos:
                epic_path = self._epic_repo_path(benchmark_name)
                shutil.rmtree(epic_path, ignore_errors=True)

            if not self.keep_simulation_outputs:
                sim_out_path = self._sim_out_dir_path(benchmark_name)
                shutil.rmtree(sim_out_path, ignore_errors=True)

            if not self.keep_reconstruction_outputs:
                recon_out_path = self._recon_out_dir_path(benchmark_name)
                shutil.rmtree(recon_out_path, ignore_errors=True)

            sim_temp_path = self._sim_temp_dir_path(benchmark_name)
            shutil.rmtree(sim_temp_path, ignore_errors=True)

            recon_temp_path = self._recon_temp_dir_path(benchmark_name)
            shutil.rmtree(recon_temp_path, ignore_errors=True)


    #Common App Definitions

    def clone_epic_cmd(self, benchmark_name : str, future : AppFuture):
        epic_path = self._epic_repo_path(benchmark_name)
        clone_cmd = f'git clone {EPIC_REPO_URL} "{epic_path}"'
        return clone_cmd

    @bash_app
    def clone_epic_app(self, benchmark_name : str, future : AppFuture):
        return self.clone_epic_cmd(benchmark_name, future)

    @bash_app
    def containerized_clone_epic_app(self, benchmark_name : str, future : AppFuture):
        return containerize(self.clone_epic_cmd(benchmark_name, future))

    def checkout_branch_cmd(self, benchmark_name : str, future : AppFuture):
        epic_path = self._epic_repo_path(self._benchmark_name)
        benchmark_config = self._get_benchmark_config(benchmark_name)
        branch = benchmark_config.epic_branch
        checkout_cmd = f'git -C "{epic_path}" checkout "{branch}"'
        return checkout_cmd

    @bash_app
    def checkout_branch_app(self, benchmark_name : str, future : AppFuture):
        return self.checkout_epic_cmd(benchmark_name, future)

    @bash_app
    def containerized_checkout_branch_app(self, benchmark_name : str, future : AppFuture):
        return containerize(self.checkout_branch_cmd(benchmark_name, future))

    @python_app
    def load_detector_configs_app(self, benchmark_name : str, future : AppFuture):
        return self.benchmark_suite_config.apply_detector_configs(benchmark_name, self.working_directory)

    def compile_epic_cmd(self, benchmark_name : str, future : AppFuture, nthreads : int = 1):

        epic_path = self._epic_repo_path(benchmark_name)
        cd_epic_cmd = f'cd "{epic_path}"'
        compile_part_one_cmd = 'cmake --fresh -B build -S . -DCMAKE_INSTALL_PREFIX=install'
        compile_part_two_cmd = f'cmake --build build -- install -j{nthreads}'
        concatenated_cmd = concatenate_commands(cd_epic_cmd, compile_part_one_cmd, compile_part_two_cmd)
        return concatenated_cmd

    @bash_app
    def compile_epic_app(self, benchmark_name : str, future : AppFuture, nthreads : int = 1):
        return self.compile_epic_cmd(benchmark_name, future, nthreads=nthreads)

    @bash_app
    def containerized_compile_epic_app(self, benchmark_name : str, future : AppFuture, nthreads : int = 1):
        return containerize(self.compile_epic_cmd(benchmark_name, future, nthreads=nthreads))


    def run_simulation_cmd(self, benchmark_name : str, simulation_name : str, future : AppFuture):

        npsim_cmd = self._npsim_cmd(benchmark_name, simulation_name)
        return npsim_cmd

    @bash_app
    def run_simulation_app(self, benchmark_name : str, simulation_name : str, future : AppFuture):
        return self.run_simulation_cmd(benchmark_name, simulation_name, future)

    @bash_app
    def containerized_run_simulation_app(self, benchmark_name : str, future : AppFuture):
        return containerize(self.compile_epic_cmd(benchmark_name, future))

    def run_reconstruction_cmd(self, benchmark_name : str, simulation_name : str, future : AppFuture):

        eicrecon_cmd = self._eicrecon_cmd(benchmark_name, simulation_name)
        return eicrecon_cmd

    @bash_app
    def run_reconstruction_app(self, benchmark_name : str, simulation_name : str, future : AppFuture):
        return self.run_reconstruction_cmd(benchmark_name, simulation_name, future)

    @bash_app
    def containerized_run_reconstruction_app(self, benchmark_name : str, simulation_name : str, future : AppFuture):
        return containerize(self.run_reconstruction_cmd(benchmark_name, simulation_name, future))


    #Helper methods for using the Benchmark Suite Configuration

    def _benchmark_names(self):

        return self.benchmark_suite_config.benchmark_names()

    def _simulation_names(self, benchmark_name : str):

        return self.benchmark_suite_config.simulation_names(benchmark_name)

    def _get_benchmark_config(self, benchmark_name : str) -> BenchmarkConfig:

        return self.benchmark_suite_config.get_benchmark_config(benchmark_name)

    def _get_simulation_config(self, benchmark_name : str, simulation_name : str) -> SimulationConfig:

        return self.benchmark_suite_config.get_simulation_config(benchmark_name, simulation_name)

    def _npsim_command_str(self, benchmark_name : str, simulation_name : str) -> str:

        return self.benchmark_suite_config.npsim_command_str(benchmark_name, simulation_name)

    def _eicrecon_command_str(self, benchmark_name : str,  simulation_name : str) -> str:

        return self.benchmark_suite_config.eicrecon_command_str(benchmark_name, simulation_name)

    def _apply_detector_configs(self, benchmark_name : str):

        return self.benchmark_suite_config.apply_detector_configs(benchmark_name, self.working_directory)

    def _benchmark_dir_path(self, benchmark_name : str) -> Path:

        return self.benchmark_suite_config.benchmark_dir_path(benchmark_name, self.working_directory)

    def _epic_repo_path(self, benchmark_name : str) -> Path:

        return self.benchmark_suite_config.epic_repo_path(benchmark_name, self.working_directory)

    def _simulation_out_dir_path(self, benchmark_name : str) -> Path:

        return self.benchmark_suite_config.simulation_out_dir_path(benchmark_name, self.working_directory)

    def _reconstruction_out_dir_path(self, benchmark_name : str) -> Path:

        return self.benchmark_suite_config.reconstruction_out_dir_path(benchmark_name, self.working_directory)

    def _analysis_out_dir_path(self, benchmark_name : str) -> Path:

        return self.benchmark_suite_config.analysis_out_dir_path(benchmark_name, self.working_directory)

    def _simulation_out_file_path(self, benchmark_name : str, simulation_name : str) -> Path:

        return self.benchmark_suite_config.simulation_out_file_path(benchmark_name, simulation_name, self.working_directory)

    def _reconstruction_out_file_path(self, benchmark_name : str, simulation_name : str) -> Path:

        return self.benchmark_suite_config.reconstruction_out_file_path(benchmark_name, simulation_name, self.working_directory)

    def _simulation_temp_dir_path(self, benchmark_name : str) -> Path:

        return self.benchmark_suite_config.simulation_temp_dir_path(benchmark_name, self.working_directory)

    def _reconstruction_temp_dir_path(self, benchmark_name : str) -> Path:

        return self.benchmark_suite_config.reconstruction_temp_dir_path(benchmark_name, self.working_directory)

    def _detector_build_path(self, benchmark_name : str, simulation_name : str) -> Path:

        return self.benchmark_suite_config.detector_build_path(benchmark_name, simulation_name, self.working_directory)

    def _npsim_cmd(self, benchmark_name : str, simulation_name : str) -> str:
        return self.benchmark_suite_config.npsim_cmd(benchmark_name, simulation_name, self.working_directory)

    def _eicrecon_cmd(self, benchmark_name : str, simulation_name : str) -> str:
        return self.benchmark_suite_config.eicrecon_cmd(benchmark_name, simulation_name, self.working_directory)








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
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3))

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

    def add_output_pipe(self, out_path):

        self.workflow_manager.add_output_pipe(out_path)

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

            #Pull shifter image if specified
            pull_container_future = None
            if self.workflow_manager.has_container():
                pull_container_future = pull_image(self.workflow_manager)
            
            for benchmark_name in incomplete_benchmark_names:

                #Get lists of incomplete tasks to complete:
                incomplete_npsim_names = incomplete_tasks.get_incomplete_npsims(benchmark_name)
                incomplete_eicrecon_names = incomplete_tasks.get_incomplete_eicrecons(benchmark_name)
                incomplete_analysis_names = incomplete_tasks.get_incomplete_analyses(benchmark_name)

                #if only analyses need to be complete, do not setup the epic repository as it is redundant in this workflow
                if len(incomplete_npsim_names) + len(incomplete_eicrecon_names) == 0:
                    for analysis_name in incomplete_analysis_names:
                        analysis_future = save_performance_plot(self.workflow_manager, benchmark_name, analysis_name, pull_container_future)
                        final_futures.append(analysis_future)
                
                else:
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

                    npsim_futures_map = {}
                    for npsim_name in incomplete_npsim_names:
                        npsim_future = run_simulations(self.workflow_manager, benchmark_name, npsim_name, compile_future)
                        npsim_futures_map[npsim_name] = npsim_future

                    eicrecon_futures_map = {}
                    for eicrecon_name in incomplete_eicrecon_names:
                        if eicrecon_name in npsim_futures_map.keys():
                            eicrecon_dependence_future = npsim_futures_map[eicrecon_name]
                        else:
                            eicrecon_dependence_future = compile_future
                        eicrecon_future = run_reconstructions(self.workflow_manager, benchmark_name, eicrecon_name, eicrecon_dependence_future, nthreads)
                        eicrecon_futures_map[eicrecon_name] = eicrecon_future

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
                self.workflow_manager.cleanup_workflow()
            finally:
                parsl.dfk().cleanup()
