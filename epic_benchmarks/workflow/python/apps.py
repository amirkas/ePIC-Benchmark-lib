from parsl import python_app
from epic_benchmarks.workflow.python.methods import (apply_detector_configs)

apply_detector_configs_app = python_app(apply_detector_configs)