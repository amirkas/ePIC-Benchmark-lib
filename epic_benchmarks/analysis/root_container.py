from typing import List, Any
import uproot as up
import pandas as pd

class RootContainer:

    file_paths : List[str]
    root_files : List[Any]
    root_dataframes : List[Any]

    def __init__(self, *root_file_paths : str):

        self.file_paths = list(root_file_paths)
        self.root_files = [up.open(file_path) for file_path in root_file_paths]
        

