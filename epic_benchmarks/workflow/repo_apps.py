from parsl import python_app, bash_app, AUTO_LOGNAME
from epic_benchmarks.workflow.manager import ParslWorkflowManager

@bash_app
def pull_image(manager : ParslWorkflowManager, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME):
    pull_cmd_str = manager.pull_shifter_cmd_str()
    return pull_cmd_str

@bash_app
def clone_epic(benchmark_name : str, manager : ParslWorkflowManager, future, remote_url="https://github.com/eic/epic.git", stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME):
    epic_path = manager.epic_dir_path(benchmark_name)
    clone_cmd = 'git clone {url} "{dir}"'.format(url=remote_url, dir=epic_path)
    return clone_cmd

@bash_app
def checkout_branch(benchmark_name : str, manager : ParslWorkflowManager, future, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME):
    
    epic_path = manager.epic_dir_path(benchmark_name)
    branch = manager.get_benchmark_epic_branch(benchmark_name)
    checkout_cmd = f'git -C "{epic_path}" checkout "{branch}"'
    return checkout_cmd

@python_app
def load_detector_configs(benchmark_name : str, manager : ParslWorkflowManager, future, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME):
    import epic_benchmarks.workflow.detector_editor as de

    de.edit_all_detectors(manager, benchmark_name=benchmark_name)

@bash_app
def compile_epic(benchmark_name : str, manager : ParslWorkflowManager, future, nthreads : int, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME):
    
    epic_path = manager.epic_dir_path(benchmark_name)
    to_epic_dir_cmd = manager.change_directory_str(epic_path)
    compile_cmd_2 = 'cmake --fresh -B build -S . -DCMAKE_INSTALL_PREFIX=install'
    compile_cmd_3 = f'cmake --build build -- install -j{nthreads}'
    cmd_list = [to_epic_dir_cmd, compile_cmd_2, compile_cmd_3]
    if manager.has_container():
        wrapped_cmd = manager.shifter_wrapper_str(cmd_list)
        return wrapped_cmd
    else:
        wrapped_cmd = manager.concatenate_commands(cmd_list)
    return wrapped_cmd




