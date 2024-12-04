from parsl import bash_app,AUTO_LOGNAME
from epic_benchmarks.ParslApp.workflow_manager import ParslWorkflowManager

@bash_app
def run_simulations(manager : ParslWorkflowManager, benchmark_name : str, simulation_name : str, future, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME):
    from epic_benchmarks.ConfigUtils.SimulationConfig import simulation_config_to_npsim_arg
    

    detector_path = manager.detector_build_path(benchmark_name)
    common_simulation_config = manager.get_common_simulation_config(benchmark_name)
    curr_simulation_config = manager.get_simulation_config(benchmark_name, simulation_name)
    output_path = manager.simulation_output_file_path(benchmark_name, simulation_name)

    source_cmd = manager.source_epic_str(benchmark_name)
    to_npsim_env_dir_str = manager.change_directory_str(manager.simulation_environment_dir_path(benchmark_name, simulation_name))
    npsim_cmd = simulation_config_to_npsim_arg(output_path, common_simulation_config, curr_simulation_config, detector_path)
    cmd_list = [source_cmd, to_npsim_env_dir_str, npsim_cmd]

    wrapped_cmd = manager.shifter_wrapper_str(cmd_list)
    return wrapped_cmd

@bash_app
def run_reconstructions(manager : ParslWorkflowManager, benchmark_name : str, simulation_name : str, future, nthreads : int, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME):
    from epic_benchmarks.ConfigUtils.SimulationConfig import simulation_config_to_eicrecon_arg

    detector_path = manager.detector_build_path(benchmark_name)
    common_simulation_config = manager.get_common_simulation_config(benchmark_name)
    curr_simulation_config = manager.get_simulation_config(benchmark_name, simulation_name)
    input_path = manager.simulation_output_file_path(benchmark_name, simulation_name)
    output_path = manager.reconstruction_output_file_path(benchmark_name, simulation_name)

    source_cmd = manager.source_epic_str(benchmark_name)
    to_eicrecon_env_dir_str = manager.change_directory_str(manager.reconstruction_environment_dir_path(benchmark_name, simulation_name))
    npsim_cmd = simulation_config_to_eicrecon_arg(input_path, output_path, common_simulation_config, curr_simulation_config, detector_path, nthreads)
    cmd_list = [source_cmd, to_eicrecon_env_dir_str, npsim_cmd]

    wrapped_cmd = manager.shifter_wrapper_str(cmd_list)
    return wrapped_cmd
    