from parsl import AUTO_LOGNAME
from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.workflow.bash.utils import concatenate_commands, source_epic_command

EPIC_REPO_URL = "https://github.com/eic/epic.git"
DEFAULT_MAT_MAP_NEVENTS = 1000

def clone_epic(workflow_config : WorkflowConfig, benchmark_name : str, **kwargs) -> str:

    epic_directory_path = workflow_config.paths.epic_repo_path(benchmark_name)
    clone_command = f'git clone {EPIC_REPO_URL} "{epic_directory_path}"'
    return clone_command

def checkout_epic_branch(workflow_config : WorkflowConfig, benchmark_name : str, **kwargs) -> str:

    epic_directory_path = workflow_config.paths.epic_repo_path(benchmark_name)
    branch = workflow_config.executor.epic_branch(benchmark_name)
    checkout_command = f'git -C "{epic_directory_path}" checkout "{branch}"'
    return checkout_command

def compile_epic(
        workflow_config : WorkflowConfig, benchmark_name : str, num_threads : int = 1, **kwargs) -> str:

    epic_directory_path = workflow_config.paths.epic_repo_path(benchmark_name)
    change_directory_cmd = f'cd {epic_directory_path}'
    compile_pt_one_cmd = 'cmake -B build -S . -DCMAKE_INSTALL_PREFIX=install'
    compile_pt_two_cmd = f'cmake --build build -- install -j {num_threads}'
    all_commands = concatenate_commands(change_directory_cmd, compile_pt_one_cmd, compile_pt_two_cmd)
    return all_commands

def generate_material_map(
        workflow_config : WorkflowConfig,
        benchmark_name : str,
        n_events=DEFAULT_MAT_MAP_NEVENTS,
        keep_root_files : bool = False, **kwargs) -> str:
    
    benchmark_config = workflow_config.benchmark_config(benchmark_name)
    if not benchmark_config.generate_material_map:
        echo_cmd =  f"echo 'No simulation for benchmark {benchmark_config.name} uses a material map. I will do nothing.'"
        return echo_cmd
    
    source_command = source_epic_command(workflow_config, benchmark_name)
    material_map_dir = workflow_config.paths.material_map_dir_path(benchmark_name)
    change_directory_cmd = f'cd {material_map_dir}'
    material_map_script_path = str(workflow_config.paths.material_map_script_path(benchmark_name))
    if not material_map_script_path.startswith("/"):
        material_map_script_path = f'./{material_map_script_path}'
    material_map_script_path = f'{material_map_script_path} --nevents={n_events}'
    run_mat_map_script_cmd = material_map_script_path
    if not keep_root_files:
        delete_mat_map_root_outputs = 'rm *.root'
        all_commands = concatenate_commands(source_command, change_directory_cmd, run_mat_map_script_cmd, delete_mat_map_root_outputs)
    else:
        all_commands = concatenate_commands(source_command, change_directory_cmd, run_mat_map_script_cmd)
    return all_commands
    

    
    


    
