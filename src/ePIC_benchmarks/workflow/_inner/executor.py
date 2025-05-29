import shutil
from multiprocessing import Pool
from typing import Optional, Sequence, Callable
from ePIC_benchmarks.workflow.config import WorkflowConfig
from ePIC_benchmarks.workflow.future import WorkflowFuture
from ePIC_benchmarks.container.containers import ContainerUnion
from ePIC_benchmarks.workflow.run import execute_workflow

WorkflowScript = Callable[[WorkflowConfig], WorkflowFuture]
class WorkflowExecutor:

    parent : WorkflowConfig

    def __init__(self, parent):
        assert(isinstance(parent, WorkflowConfig))
        self.parent = parent

    def epic_branch(self, benchmark_name : str) -> str:

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.epic_branch
    
    def get_all_containers(self) -> Sequence[ContainerUnion]:

        return self.parent.parsl_config.all_containers()
    
    def get_container(self, executor_label) -> Optional[ContainerUnion]:
        
        return self.parent.parsl_config.executor_container(executor_label)
    
    def run_benchmarks(
        self, workflow : WorkflowConfig, script_func : Optional[WorkflowScript] = None,
        script_path : Optional[str] = None, script_func_name : Optional[str] = None) -> None:
    
        return execute_workflow(workflow, script_func=script_func, script_path=script_path, script_func_name=script_func_name)


    def apply_detector_configs(self, benchmark_name : str):

        benchmark_config = self.parent.benchmark_config(benchmark_name)
        benchmark_config.apply_detector_configs(self.parent.paths.workflow_dir_path)

    def npsim_command_string(self, benchmark_name : str, simulation_name : str) -> str:
        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.npsim_cmd(simulation_name, self.parent.paths.workflow_dir_path)

    def eicrecon_command_string(self, benchmark_name : str, simulation_name : str) -> str:
        benchmark_config = self.parent.benchmark_config(benchmark_name)
        return benchmark_config.eicrecon_cmd(simulation_name, self.parent.paths.workflow_dir_path)

    def init_benchmark_directory(self, benchmark_name):

        benchmark_config = self.parent.benchmark_config(benchmark_name)

        benchmark_dir_path = self.parent.paths.benchmark_dir_path(benchmark_name)
        if self.parent.redo_all_benchmarks:
            shutil.rmtree(benchmark_dir_path, ignore_errors=True)
        benchmark_dir_path.mkdir(parents=True, exist_ok=True)

        epic_path = self.parent.paths.epic_repo_path(benchmark_name)
        
        if self.parent.redo_epic_building:
            shutil.rmtree(epic_path, ignore_errors=True)
        epic_path.mkdir(parents=True, exist_ok=True)
        
        #Copy existing ePIC Repository to Benchmark ePIC Dir if it is not None
        if benchmark_config.existing_epic_directory_path is not None:
            existing_epic_path = benchmark_config.existing_epic_directory_path
            shutil.copytree(existing_epic_path, epic_path, dirs_exist_ok=True)

        analysis_path = self.parent.paths.analysis_out_dir_path(benchmark_name)
        if self.parent.redo_analysis:
            shutil.rmtree(analysis_path, ignore_errors=True)
        analysis_path.mkdir(parents=True, exist_ok=True)

        sim_out_dir_path = self.parent.paths.simulation_out_dir_path(benchmark_name)
        sim_temp_dir_path = self.parent.paths.simulation_temp_dir_path(benchmark_name)
        if self.parent.redo_simulations:
            shutil.rmtree(sim_out_dir_path, ignore_errors=True)
            shutil.rmtree(sim_temp_dir_path, ignore_errors=True)
        sim_out_dir_path.mkdir(parents=True, exist_ok=True)
        sim_temp_dir_path.mkdir(parents=True, exist_ok=True)

        recon_out_dir_path = self.parent.paths.reconstruction_out_dir_path(benchmark_name)
        recon_temp_dir_path = self.parent.paths.reconstruction_temp_dir_path(benchmark_name)
        if self.parent.redo_reconstructions:
            shutil.rmtree(recon_out_dir_path, ignore_errors=True)
            shutil.rmtree(recon_temp_dir_path, ignore_errors=True)

        recon_out_dir_path.mkdir(parents=True, exist_ok=True)
        recon_temp_dir_path.mkdir(parents=True, exist_ok=True)

        #Initialize temporary directory for each npsim and eicrecon execution  
        for simulation_name in self.parent.simulation_names(benchmark_name):
            simulation_instance_temp_path = self.parent.paths.simulation_instance_temp_dir_path(benchmark_name, simulation_name)
            simulation_instance_temp_path.mkdir(parents=True, exist_ok=True)

            reconstruction_instance_temp_path = self.parent.paths.reconstruction_instance_temp_dir_path(benchmark_name, simulation_name)
            reconstruction_instance_temp_path.mkdir(parents=True, exist_ok=True)

    def init_directories(self):

        benchmark_suite_path = self.parent.paths.workflow_dir_path
        benchmark_suite_path.mkdir(parents=True, exist_ok=True)

        benchmark_names = self.parent.benchmark_names()

        pool = Pool(len(benchmark_names))

        try:
            pool.map(self.init_benchmark_directory, benchmark_names)
        except:
            pool.close()
            pool.join()


        # for benchmark_name in self.parent.benchmark_names():



            # benchmark_dir_path = self.parent.paths.benchmark_dir_path(benchmark_name)
            # if self.parent.redo_all_benchmarks:
            #     shutil.rmtree(benchmark_dir_path, ignore_errors=True)
            # benchmark_dir_path.mkdir(parents=True, exist_ok=True)

            # epic_path = self.parent.paths.epic_repo_path(benchmark_name)
            # if self.parent.redo_epic_building:
            #     shutil.rmtree(epic_path, ignore_errors=True)
            # epic_path.mkdir(parents=True, exist_ok=True)

            # analysis_path = self.parent.paths.analysis_out_dir_path(benchmark_name)
            # if self.parent.redo_analysis:
            #     shutil.rmtree(epic_path, ignore_errors=True)
            # analysis_path.mkdir(parents=True, exist_ok=True)

            # sim_out_dir_path = self.parent.paths.simulation_out_dir_path(benchmark_name)
            # sim_temp_dir_path = self.parent.paths.simulation_temp_dir_path(benchmark_name)
            # if self.parent.redo_simulations:
            #     shutil.rmtree(sim_out_dir_path, ignore_errors=True)
            #     shutil.rmtree(sim_temp_dir_path, ignore_errors=True)
            # sim_out_dir_path.mkdir(parents=True, exist_ok=True)
            # sim_temp_dir_path.mkdir(parents=True, exist_ok=True)

            # recon_out_dir_path = self.parent.paths.reconstruction_out_dir_path(benchmark_name)
            # recon_temp_dir_path = self.parent.paths.reconstruction_temp_dir_path(benchmark_name)
            # if self.parent.redo_reconstructions:
            #     shutil.rmtree(recon_out_dir_path, ignore_errors=True)
            #     shutil.rmtree(recon_temp_dir_path, ignore_errors=True)

            # recon_out_dir_path.mkdir(parents=True, exist_ok=True)
            # recon_temp_dir_path.mkdir(parents=True, exist_ok=True)

            # #Initialize temporary directory for each npsim and eicrecon execution  
            # for simulation_name in self.parent.simulation_names(benchmark_name):
            #     simulation_instance_temp_path = self.parent.paths.simulation_instance_temp_dir_path(benchmark_name, simulation_name)
            #     simulation_instance_temp_path.mkdir(parents=True, exist_ok=True)

            #     reconstruction_instance_temp_path = self.parent.paths.reconstruction_instance_temp_dir_path(benchmark_name, simulation_name)
            #     reconstruction_instance_temp_path.mkdir(parents=True, exist_ok=True)

    def cleanup_directories(self):

        for benchmark_name in self.parent.benchmark_names():

            if not self.parent.keep_epic_repos:
                epic_path = self.parent.paths.epic_repo_path(benchmark_name)
                shutil.rmtree(epic_path, ignore_errors=True)

            if not self.parent.keep_simulation_outputs:
                sim_out_dir_path = self.parent.paths.simulation_out_dir_path(benchmark_name)
                shutil.rmtree(sim_out_dir_path, ignore_errors=True)

            if not self.parent.keep_reconstruction_outputs:
                recon_out_dir_path = self.parent.paths.reconstruction_out_dir_path(benchmark_name)
                shutil.rmtree(recon_out_dir_path, ignore_errors=True)

            if not self.parent.keep_analysis_outputs:
                analysis_out_path = self.parent.paths.analysis_out_dir_path(benchmark_name)
                shutil.rmtree(analysis_out_path, ignore_errors=True)

            sim_temp_dir_path = self.parent.paths.simulation_temp_dir_path(benchmark_name)
            shutil.rmtree(sim_temp_dir_path, ignore_errors=True)

            recon_temp_dir_path = self.parent.paths.reconstruction_temp_dir_path(benchmark_name)
            shutil.rmtree(recon_temp_dir_path, ignore_errors=True)

