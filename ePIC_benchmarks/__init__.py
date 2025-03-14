from . import (analysis, benchmark, container, detector, parsl, simulation, workflow)
from .workflow._run import run_from_file_path
import argparse

__all__ = ['analysis', 'benchmark', 'container', 'detector', 'parsl', 'simulation', 'workflow']

if __name__ == '__main__':

    parser = argparse.ArgumentParser("ePIC Simulation Workflow")
    parser.add_argument("-c", "--config", help="Absolute path or relative path to the workflow configiration file")
    parser.add_argument("-s", "--script", help="Path to the workflow task script")

    run_from_file_path(config_path=parser.config, script_path=parser.script)