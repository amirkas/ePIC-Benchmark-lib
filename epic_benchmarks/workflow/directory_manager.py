from abc import abstractmethod
from typing import Dict, Union, List

from pydantic import BaseModel, Field
import shutil
import os

class BaseDirectoryManager(BaseModel):

    benchmark_simulation_map : Dict[str, Union[List[str], str]] = Field(default_factory=dict, init=True)

    @abstractmethod
    def workflow_root_dir(self):

        raise NotImplementedError()

    @abstractmethod
    def epic_repo_dir(self, benchmark_name : str, simulation_name : str) -> str:

        raise NotImplementedError()

    @abstractmethod
    def epic_detector_dir(self, benchmark_name : str, simulation_name : str) -> str:

        raise NotImplementedError()

    @abstractmethod
    def simulation_output_dir(self, benchmark_name : str, simulation_name : str) -> str:

        raise NotImplementedError()

    @abstractmethod
    def reconstruction_output_dir(self, benchmark_name : str, simulation_name : str) -> str:

        raise NotImplementedError()

    @abstractmethod
    def analysis_output_dir(self, benchmark_name : str, simulation_name : str) -> str:

        raise NotImplementedError()

    @abstractmethod
    def simulation_temp_dir(self, benchmark_name : str, simulation_name : str) -> str:

        raise NotImplementedError()

    @abstractmethod
    def reconstruction_temp_dir(self, benchmark_name : str, simulation_name : str) -> str:

        raise NotImplementedError()

    @classmethod
    def file_path(cls, directory_path : str, filename : str) -> str:

        return os.path.join(directory_path, filename)

    def init_directories(self, override : bool) -> None:

        if override:

            for benchmark_name, simulation_names in self.benchmark_simulation_map.items():
                if isinstance(simulation_names, str):
                    self._remove_all_dirs_recursive(benchmark_name, simulation_names)
                else:
                    for simulation_name in simulation_names:
                        self._remove_all_dirs_recursive(benchmark_name, simulation_name)






    def cleanup_directories(self, remove_epic_repo : bool , remove_temp_dirs: bool) -> None:


        pass

    def _remove_all_dirs_recursive(self, benchmark_name : str, simulation_name : str) -> None:

        self._remove_dir_recursive(self.epic_repo_dir(benchmark_name, simulation_name))
        self._remove_dir_recursive(self.epic_detector_dir(benchmark_name, simulation_name))
        self._remove_dir_recursive(self.simulation_output_dir(benchmark_name, simulation_name))
        self._remove_dir_recursive(self.reconstruction_output_dir(benchmark_name, simulation_name))
        self._remove_dir_recursive(self.analysis_output_dir(benchmark_name, simulation_name))
        self._remove_dir_recursive(self.simulation_temp_dir(benchmark_name, simulation_name))
        self._remove_dir_recursive(self.reconstruction_temp_dir(benchmark_name, simulation_name))

    @classmethod
    def _remove_dir_recursive(cls, dir_path : str):

        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)