from ePIC_benchmarks.workflow.python import python_app
from ePIC_benchmarks.workflow.python.methods.analysis import (generate_performance_plots)

generate_performance_plots_app = python_app(generate_performance_plots)