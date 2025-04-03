from .workflow.config import WorkflowConfig
from .workflow.run import convert_to_abs_path, execute_workflow
import argparse
import os

if __name__ == "__main__":

    CWD = os.getcwd()

    parser = argparse.ArgumentParser("ePIC Workflow entry point")
    parser.add_argument("workflow_config_path", default=os.path.join(CWD, "workflow_config.yml"))
    parser.add_argument("--script", "-s", default=os.path.join(CWD, "workflow_script.py"))
    parser.add_argument("--funcName", "-f", default="run")

    args = parser.parse_args()
    config_path = convert_to_abs_path(args.workflow_config_path, CWD)
    script_path = convert_to_abs_path(args.script, CWD)
    func_name = args.funcName

    if not os.path.exists(config_path):
        err = f"Workflow config file at '{config_path}' does not exist"
        raise ValueError(err)
    
    if not os.path.exists(script_path):
        err = f"Workflow script file at '{script_path}' does not exist"
        raise ValueError(err)
    
    if len(func_name) == 0:
        err = f"Workflow script function name must be a string with length > 1"
        raise ValueError(err)
    
    workflow_config = WorkflowConfig.load_from_file(config_path)
    execute_workflow(workflow_config, script_path=script_path, func_name=func_name)