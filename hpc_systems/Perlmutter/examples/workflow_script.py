from typing import List
from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.parsl.types import FutureType
from ePIC_benchmarks.workflow.bash import bash_app
from ePIC_benchmarks.workflow.python import python_app
from ePIC_benchmarks.workflow.bash.methods.container import pull_containers
from ePIC_benchmarks.workflow.bash.methods.epic import clone_epic, checkout_epic_branch, compile_epic, generate_material_map
from ePIC_benchmarks.workflow.bash.methods.simulation import run_npsim, run_eicrecon
from ePIC_benchmarks.workflow.python.methods.detector import apply_detector_configs
from ePIC_benchmarks.container import ShifterConfig

eicshell_container = ShifterConfig(
    entry_point="/opt/local/bin/eic-shell",
    image="eicweb/jug_xl:25.02.0-stable",
    entry_command="source activate parsl;"
)

clone_epic_app = bash_app(clone_epic, executors=['Headless_Executor'])
pull_containers_app = bash_app(pull_containers, executors=['Headless_Executor'])
checkout_app = bash_app(checkout_epic_branch, executors=['Headless_Executor'])
compile_epic_app = bash_app(compile_epic, executors=['Headless_Executor'], container=eicshell_container)
run_npsim_app = bash_app(run_npsim, executors=['Headless_Executor'], container=eicshell_container)
run_eicrecon_app = bash_app(run_eicrecon, executors=['Headless_Executor'], container=eicshell_container)
generate_material_map_app = bash_app(generate_material_map, executors=['Headless_Executor'], container=eicshell_container)
apply_detector_configuration_app = python_app(apply_detector_configs, executors=['Headless_Executor'])

def run(config : WorkflowConfig, futures : List[FutureType]):

    containers = config.parsl_config.all_containers()
    pull_containers_future = pull_containers_app(*containers)
    futures.append(pull_containers_future)

    for benchmark_name in config.benchmark_names():
            
            clone_epic_future = clone_epic_app(config, benchmark_name, inputs=[pull_containers_future])
            futures.append(clone_epic_future)

            checkout_branch_future = checkout_app(config, benchmark_name, inputs=[clone_epic_future])
            futures.append(checkout_branch_future)

            update_detectors_future = apply_detector_configuration_app(config, benchmark_name, inputs=[checkout_branch_future])
            futures.append(update_detectors_future)

            compile_epic_future = compile_epic_app(config, benchmark_name, num_threads=4,inputs=[update_detectors_future])
            futures.append(compile_epic_future)

            gen_material_map_future = generate_material_map_app(config, benchmark_name, n_events=100, inputs=[compile_epic_future])
            futures.append(gen_material_map_future)

            for simulation_name in config.simulation_names(benchmark_name):
                                    
                  run_npsim_future = run_npsim_app(config, benchmark_name, simulation_name, inputs=[compile_epic_future])
                  futures.append(run_npsim_future)

                  run_eicrecon_future = run_eicrecon_app(config, benchmark_name, simulation_name, use_generated_material_map=True, inputs=[gen_material_map_future, run_npsim_future])
                  futures.append(run_eicrecon_future)

    


