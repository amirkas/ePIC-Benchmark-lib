from typing import Optional
from ePIC_benchmarks._file.types import PathType
from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.workflow._inner.executor import WorkflowScript

WORKFLOW_CONFIG : Optional[WorkflowConfig] = None

def load_from_file_path(config_path : PathType):
    global WORKFLOW_CONFIG
    try:
        WORKFLOW_CONFIG = WorkflowConfig.load_from_file(config_path)
    except Exception as e:
        print(f"Could not load workflow config from path '{config_path}'")
        raise e
    
def load_from_config(config : WorkflowConfig):
    global WORKFLOW_CONFIG
    WORKFLOW_CONFIG = config

def run_deprecated(script_path : Optional[str] = None):
    global WORKFLOW_CONFIG
    if WORKFLOW_CONFIG is None:
        raise RuntimeError("A workflow configuration must be loaded before running")
    if (isinstance(WORKFLOW_CONFIG.script_path, PathType) and len(str(WORKFLOW_CONFIG.script_path)) > 0):
        script_path = WORKFLOW_CONFIG.script_path

    WORKFLOW_CONFIG.executor.run_benchmarks(script_path)

def run(script_func : Optional[WorkflowScript] = None):
    
    global WORKFLOW_CONFIG
    if WORKFLOW_CONFIG is None:
        raise RuntimeError("A workflow configuration must be loaded before running")
    if WORKFLOW_CONFIG.workflow_script is not None and callable(WORKFLOW_CONFIG.workflow_script):
        script_func = WORKFLOW_CONFIG.workflow_script
    # if (isinstance(WORKFLOW_CONFIG.workflow_script, PathType) and len(str(WORKFLOW_CONFIG.script_path)) > 0):
    #     script_path = WORKFLOW_CONFIG.script_path
    WORKFLOW_CONFIG.executor.run_benchmarks(script_func=script_func)


def run_from_file_path(config_path : PathType, script_func : Optional[WorkflowScript] = None, script_path : Optional[str] = None):

    load_from_file_path(config_path)
    run(script_func=script_func)

def run_from_config(config : WorkflowConfig, script_func : Optional[WorkflowScript] = None, script_path : Optional[str] = None):

    load_from_config(config)

    run(script_func=script_func)



    