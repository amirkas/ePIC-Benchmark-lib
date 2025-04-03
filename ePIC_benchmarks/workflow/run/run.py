import argparse
import parsl
import os
from typing import Callable, Optional
from parsl import Config
from parsl.configs.local_threads import config
from parsl.utils import get_all_checkpoints
from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.workflow.future import WorkflowFuture
from ePIC_benchmarks.workflow._inner.executor import get_workflow_script_func
from ePIC_benchmarks.workflow.join import join_app

def convert_to_abs_path(path : str, cwd : str):

    if not os.path.isabs(path):
        return os.path.join(cwd, path)
    return path

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

        #Initialize any uninitialized directories
        workflow.executor.init_directories()

        #Set checkpointing mode to checkpoint on task exit.
        # config.checkpoint_mode = "task_exit"

        #If workflow is not being redone, start from the last recorded checkpoints
        if not workflow.redo_all_benchmarks:

            config.checkpoint_files = get_all_checkpoints()
        
        parsl.clear()

        #Load Provided Parsl Config
        with parsl.load(workflow.parsl_config.to_parsl_config()):

            try:

                #Execute provided workflow script to add tasks to parsl dependency graph
                try:
                    parsl_wrapped_script_func = join_app(exec_func)
                    workflow_future : WorkflowFuture = parsl_wrapped_script_func(workflow.parent)

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
                    workflow.executor.cleanup_directories()
                finally:
                    parsl.dfk().cleanup()

        parsl.clear()
