import shutil
import parsl
import importlib.util

from pathlib import Path
from typing import Optional, Sequence, Union
from parsl.configs.local_threads import config
from parsl.utils import get_all_checkpoints
from parsl.dataflow.futures import AppFuture
from parsl.app.futures import DataFuture

from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.container.containers import ContainerUnion


def run_workflow_script(script_path : PathType, workflow_config : WorkflowConfig, all_futures : Sequence[Union[AppFuture, DataFuture]]):

    path = Path(script_path).resolve()
    spec = importlib.util.spec_from_file_location("workflow", str(path))
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    #TODO: Check if run function exists and has correct signature
    return script.run(workflow_config, all_futures)

class WorkflowExecutor:

    parent : WorkflowConfig


    def __init__(self, parent):
        assert(isinstance(parent, WorkflowConfig))
        self.parent = parent

    def run_benchmarks(self, script_path : Optional[str] = None):

        #Check if script path is provided
        if script_path is None and self.parent.script_path is None:
            raise ValueError("Must provide a path to a workflow script to execute")

        #Set script path
        exec_script_path = script_path if script_path is not None else self.parent.script_path

        #Initialize any uninitialized directories
        self.init_directories()

        #Set checkpointing mode to checkpoint on task exit.
        config.checkpoint_mode = "task_exit"

        #If workflow is not being redone, start from the last recorded checkpoints
        if not self.parent.redo_all_benchmarks:

            config.checkpoint_files = get_all_checkpoints()

        #Load Provided Parsl Config
        parsl.load(self.parent.parsl_config.to_parsl_config())

        try:
            all_futures = []

            #Execute provided workflow script to add tasks to parsl dependency graph
            try:
                run_workflow_script(exec_script_path, self.parent, all_futures)
            except Exception as e:
                print(f"Could not execute script located at '{exec_script_path}'.")
                raise ValueError(e)

            #Wait for every task to complete
            for task_future in all_futures:
                assert(isinstance(task_future, AppFuture) or isinstance(task_future, DataFuture))
                task_future.result()

        except Exception as e:
            #Ensure cleanup keeps all files regardless of config settings if workflow terminates early.
            #Guarantees checkpointing will work as intended.
            self.parent.keep_epic_repos = True
            self.parent.keep_simulation_outputs = True
            self.parent.keep_reconstruction_outputs= True
            raise e

        finally:
            #Cleanup routine
            try:
                self.cleanup_directories()
            finally:
                parsl.dfk().cleanup()

    def epic_branch(self, benchmark_name : str) -> str:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.epic_branch
    
    def get_all_containers(self) -> Sequence[ContainerUnion]:

        return self.parent.parsl_config.all_containers()
    
    def get_container(self, executor_label) -> Optional[ContainerUnion]:
        
        return self.parent.parsl_config.executor_container(executor_label)

    def apply_detector_configs(self, benchmark_name : str):

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        benchmark_config.apply_detector_configs(self.parent.paths.workflow_dir_path)

    def npsim_command_string(self, benchmark_name : str, simulation_name : str) -> str:
        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.npsim_cmd(simulation_name, self.parent.paths.workflow_dir_path)

    def eicrecon_command_string(self, benchmark_name : str, simulation_name : str) -> str:
        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.eicrecon_cmd(simulation_name, self.parent.paths.workflow_dir_path)

    def init_directories(self):


        benchmark_suite_path = self.parent.paths.workflow_dir_path
        # if self.parent.redo_all_benchmarks:
        #     shutil.rmtree(benchmark_suite_path, ignore_errors=True)
        benchmark_suite_path.mkdir(parents=True, exist_ok=True)

        for benchmark_name in self.parent.benchmark_names():

            benchmark_dir_path = self.parent.paths.benchmark_dir_path(benchmark_name)
            benchmark_dir_path.mkdir(parents=True, exist_ok=True)

            epic_path = self.parent.paths.epic_repo_path(benchmark_name)
            epic_path.mkdir(parents=True, exist_ok=True)

            analysis_path = self.parent.paths.analysis_out_dir_path(benchmark_name)
            analysis_path.mkdir(parents=True, exist_ok=True)

            sim_out_dir_path = self.parent.paths.simulation_out_dir_path(benchmark_name)
            sim_out_dir_path.mkdir(parents=True, exist_ok=True)

            recon_out_dir_path = self.parent.paths.reconstruction_out_dir_path(benchmark_name)
            recon_out_dir_path.mkdir(parents=True, exist_ok=True)

            sim_temp_dir_path = self.parent.paths.simulation_temp_dir_path(benchmark_name)
            sim_temp_dir_path.mkdir(parents=True, exist_ok=True)

            recon_temp_dir_path = self.parent.paths.reconstruction_temp_dir_path(benchmark_name)
            recon_temp_dir_path.mkdir(parents=True, exist_ok=True)

            #Initialize temporary directory for each npsim and eicrecon execution  
            for simulation_name in self.parent.simulation_names(benchmark_name):
                simulation_instance_temp_path = self.parent.paths.simulation_instance_temp_dir_path(benchmark_name, simulation_name)
                simulation_instance_temp_path.mkdir(parents=True, exist_ok=True)

                reconstruction_instance_temp_path = self.parent.paths.reconstruction_instance_temp_dir_path(benchmark_name, simulation_name)
                reconstruction_instance_temp_path.mkdir(parents=True, exist_ok=True)

    def cleanup_directories(self):

        for benchmark_name in self.parent.benchmark_names():

            if not self.parent.keep_epic_repos:
                epic_path = self.parent.paths.epic_repo_path(benchmark_name)
                shutil.rmtree(epic_path, ignore_errors=True)

            if not self.parent.keep_simulation_outputs:
                sim_out_dir_path = self.parent.paths.simulation_out_dir_path(benchmark_name)
                shutil.rmtree(sim_out_dir_path, ignore_errors=True)

            if not self.parent.keep_reconstruction_outputs:
                recon_out_dir_path = self.parent.paths.reconstruction_out_dir_path(benchmark_name)
                shutil.rmtree(recon_out_dir_path, ignore_errors=True)

            if not self.parent.keep_analysis_outputs:
                analysis_out_path = self.parent.paths.analysis_out_dir_path(benchmark_name)
                shutil.rmtree(analysis_out_path, ignore_errors=True)

            sim_temp_dir_path = self.parent.paths.simulation_temp_dir_path(benchmark_name)
            shutil.rmtree(sim_temp_dir_path, ignore_errors=True)

            recon_temp_dir_path = self.parent.paths.reconstruction_temp_dir_path(benchmark_name)
            shutil.rmtree(recon_temp_dir_path, ignore_errors=True)


    