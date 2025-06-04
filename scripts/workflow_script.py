from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.workflow.bash import bash_app
from ePIC_benchmarks.workflow.python import python_app
from ePIC_benchmarks.workflow.bash.methods.container import pull_containers
from ePIC_benchmarks.workflow.bash.methods.epic import (
    clone_epic, checkout_epic_branch, compile_epic,
    generate_material_map
)
from ePIC_benchmarks.workflow.bash.methods.simulation import run_npsim, run_eicrecon
from ePIC_benchmarks.workflow.python.methods.detector import apply_detector_configs
from ePIC_benchmarks.workflow.python.methods.analysis import generate_performance_plots
from ePIC_benchmarks.container import ShifterConfig
from parsl import AUTO_LOGNAME

eicshell_container = ShifterConfig(
    entry_point="/opt/local/bin/eic-shell",
    image="eicweb/jug_xl:25.02.0-stable",
)
clone_epic_app = bash_app(clone_epic)
pull_containers_app = bash_app(pull_containers)
checkout_app = bash_app(checkout_epic_branch)
compile_epic_app = bash_app(compile_epic)
run_npsim_app = bash_app(run_npsim)
run_eicrecon_app = bash_app(run_eicrecon)
generate_material_map_app = bash_app(generate_material_map)
apply_detector_configuration_app = python_app(apply_detector_configs)
performance_analysis_app = python_app(generate_performance_plots)

def run(config : WorkflowConfig):

    final_futures = []

    pull_containers_future = pull_containers_app(eicshell_container)

    for benchmark_name in config.benchmark_names():

            clone_epic_future = clone_epic_app(config, benchmark_name, dependency=pull_containers_future)

            checkout_branch_future = checkout_app(config, benchmark_name, dependency=clone_epic_future)

            update_detectors_future = apply_detector_configuration_app(config, benchmark_name, dependency=checkout_branch_future)

            compile_epic_future = compile_epic_app(config, benchmark_name, num_threads=1, container=eicshell_container, dependency=update_detectors_future, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME)

            generate_material_map_future = generate_material_map_app(config, benchmark_name, nevents=20000, container=eicshell_container, dependency=compile_epic_future)

            for simulation_name in config.simulation_names(benchmark_name):

                run_npsim_future = run_npsim_app(config, benchmark_name, simulation_name, container=eicshell_container, dependency=compile_epic_future, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME)

                run_eicrecon_future = run_eicrecon_app(config, benchmark_name, simulation_name, use_generated_material_map=True, container=eicshell_container, dependencies=[run_npsim_future, generate_material_map_future], stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME)

                analysis_future = performance_analysis_app(
                    config, benchmark_name, simulation_name,
                    dependency=run_eicrecon_future
                )
                final_futures.append(analysis_future)

    return final_futures