import importlib
# import logging
import parsl
import os
import sys
from pathlib import Path
from typing import Callable, Optional
from parsl.configs.local_threads import config
from parsl.utils import get_all_checkpoints
from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.workflow.future import WorkflowFuture
from ePIC_benchmarks.workflow.join import join_app

# logging.basicConfig(level=logging.DEBUG)

def convert_to_abs_path(path : str, cwd : str):

    if not os.path.isabs(path):
        return os.path.join(cwd, path)
    return path

def get_workflow_script_func(script_path : PathType, func_name : str = "run"):

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
            # logging.info("Workflow script succesfully loaded")
            return run_func
    except Exception as e:
        raise e


WorkflowScript = Callable[[WorkflowConfig], WorkflowFuture]

def execute_workflow(
        workflow : WorkflowConfig, script_func : Optional[WorkflowScript] = None,
        script_path : Optional[str] = None, script_func_name : Optional[str] = None) -> None:

        #Check if script function or path is provided
        exec_script_func = script_func if script_func is not None else workflow.workflow_script
        exec_script_path = script_path if script_path is not None else workflow.script_path

        if exec_script_func is None and exec_script_path is None:
            raise ValueError("Must provide a workflow script function or workflow script path")
        
        #Prioritize script function over script file as the workflow executor
        if script_func_name:
            exec_func = exec_script_func if exec_script_func is not None else get_workflow_script_func(exec_script_path, func_name=script_func_name)
        else:
            exec_func = exec_script_func if exec_script_func is not None else get_workflow_script_func(exec_script_path)

        # logging.info("Initializing workflow directories...")

        #Initialize any uninitialized directories
        workflow.executor.init_directories()

        # logging.info("Workflow directories initialized")

        #Set checkpointing mode to checkpoint on task exit.
        config.checkpoint_mode = "task_exit"

        parsl.clear()

        #If workflow is not being redone, start from the last recorded checkpoints
        if not workflow.redo_all_benchmarks:
            # logging.info("Loading last task checkpoints")
            config.checkpoint_files = get_all_checkpoints()
        
        # logging.info("Starting the workflow")
        #Load Provided Parsl Config
        with parsl.load(workflow.parsl_config.to_parsl_config()):

            try:
                #Execute provided workflow script to add tasks to parsl dependency graph
                try:
                    parsl_wrapped_script_func = join_app(exec_func)
                    workflow_future : WorkflowFuture = parsl_wrapped_script_func(workflow)

                    #Wait for every task to complete
                    if isinstance(workflow_future, (list, set)):
                        for future in workflow_future:
                            future.result()
                    else:
                        workflow_future.result()
                except Exception as e:
                    raise e


            except Exception as e:
                #Ensure cleanup keeps all files regardless of config settings if workflow terminates early.
                #Guarantees checkpointing will work as intended.
                workflow.keep_epic_repos = True
                workflow.keep_simulation_outputs = True
                workflow.keep_reconstruction_outputs= True
                raise e

            finally:
                #Cleanup routine
                try:
                    # logging.info("Cleaning up directories")
                    workflow.executor.cleanup_directories()
                finally:
                    parsl.dfk().cleanup()

