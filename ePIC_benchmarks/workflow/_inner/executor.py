import shutil
import parsl
import importlib.util
import sys
from concurrent.futures import Future

from pathlib import Path
from typing import Optional, Sequence, Callable, Union
from parsl.configs.local_threads import config
from parsl.utils import get_all_checkpoints

from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks.workflow.config import WorkflowConfig, WorkflowScript
from ePIC_benchmarks.workflow.future import WorkflowFuture
from ePIC_benchmarks.container.containers import ContainerUnion
from ePIC_benchmarks.workflow.join import join_app
from ePIC_benchmarks.workflow.run import execute_workflow


def get_workflow_script_func(script_path : PathType, func_name : str = "run") -> WorkflowScript:

    try:
        path = Path(script_path).resolve()
        spec = importlib.util.spec_from_file_location("user_workflow", str(path))
        module = importlib.util.module_from_spec(spec)
        sys.modules["user_workflow"] = module
        spec.loader.exec_module(module)

        #TODO: Check if run function exists and has correct signature
        run_func = getattr(module, func_name, None)
        if run_func is None:
            err = f"'{func_name}' function could not be found in {script_path}"
            raise ModuleNotFoundError(err)
        elif not callable(run_func):
            err = f"'{func_name}' is not a callable function"
            raise ImportError(err)
        else:
            return run_func
    except Exception as e:
        raise e

class WorkflowExecutor:

    parent : WorkflowConfig

    def __init__(self, parent):
        assert(isinstance(parent, WorkflowConfig))
        self.parent = parent

    def epic_branch(self, benchmark_name : str) -> str:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.epic_branch
    
    def get_all_containers(self) -> Sequence[ContainerUnion]:

        return self.parent.parsl_config.all_containers()
    
    def get_container(self, executor_label) -> Optional[ContainerUnion]:
        
        return self.parent.parsl_config.executor_container(executor_label)
    
    def run_benchmarks(
        self, workflow : WorkflowConfig, script_func : Optional[WorkflowScript] = None,
        script_path : Optional[str] = None, script_func_name : Optional[str] = None) -> None:
    
        return execute_workflow(workflow, script_func=script_func, script_path=script_path, script_func_name=script_func_name)


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

