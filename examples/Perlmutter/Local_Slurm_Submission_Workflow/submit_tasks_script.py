from ePIC_benchmarks.workflow import WorkflowConfig
from ePIC_benchmarks.workflow.run import execute_workflow
from typing import Union
from pathlib import Path

#Path to the saved WorkflowConfig (Update this to the correct path for your workflow)
WORKFLOW_CONFIG_PATH : Union[str, Path] = Path.cwd().joinpath("workflow_config.yml")
#Path to the workflow script to execute
WORKFLOW_SCRIPT_PATH : Union[str, Path] = ... 
WORKFLOW_SCRIPT_FUNC_NAME : str = "run" #This must match the workflow script function name.

LOADED_WORKFLOW_CONFIG = WorkflowConfig.load_from_file(WORKFLOW_CONFIG_PATH)

#Execute the workflow, submitting jobs to the slurm scheduler
# via a task manager running on your login node.
execute_workflow(
    workflow=LOADED_WORKFLOW_CONFIG,
    script_path=WORKFLOW_SCRIPT_PATH,
    script_func_name=WORKFLOW_SCRIPT_FUNC_NAME
)

