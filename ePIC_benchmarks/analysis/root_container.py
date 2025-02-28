from abc import ABC, abstractmethod
from typing import List, Any, Optional, Self
import uproot as up
import pandas as pd

class BaseRootContainer(ABC):

    file_paths : List[str]
    root_objects : List[Any]
    curr_branch : str

    def __init__(self, *root_file_paths : str, branch_name : Optional[str] = None):

        self.file_paths = list(root_file_paths)
        if branch_name is None:
            self.root_objects = [up.open(file_path) for file_path in root_file_paths]
            self.curr_branch = ''
        else:
            self.root_objects = [up.open(file_path)[branch_name] for file_path in root_file_paths]
            self.curr_branch = branch_name

        self.preprocess()

    def container_from_branch(self, branch_name : str) -> Self:

        class_type = self.__class__
        return class_type(self.file_paths, branch_name)

    @abstractmethod
    def preprocess(self) -> None:

        pass






