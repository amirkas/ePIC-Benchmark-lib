from typing import List, Any, Optional
import pandas as pd
import awkward as ak
from epic_benchmarks.analysis.root_container import BaseRootContainer

class TrackingRootContainer(BaseRootContainer):

    root_dataframes : List[Any]
    params : List[Any]
    particles : List[Any]
    all_pions : List[Any]
    


    def __init__(self, *root_file_paths : str, k_flatten : bool = True, branch_name : Optional[str] = None):

        super().__init__(root_file_paths, branch_name)
        self.k_flatten = k_flatten

    def preprocess(self):
        
        for root_obj in self.root_objects:

            df_arr = root_obj.array(library='ak')
            df = ak.to_dataframe(df_arr)

            if isinstance(df, pd.Series):
                self.root_dataframes.append(df)
            
            columns = df.columns
            if len(columns) <= 0:
                print(f"Could not find any leaves under the branch, '{self.curr_branch}'")
                self.root_dataframes.append(pd.DataFrame())

            #Remove prefixes from column names
            columns = [str(col) for col in columns if str(col).startswith(f'{self.curr_branch}')]

            if not columns:
                self.root_dataframes.append(df)

            for col_name in columns:
                if "[" in col_name:
                    columns.remove(col_name)
                if "covariance.covariance" in col_name:
                    columns.remove(col_name)

            df = df[columns]
            df.rename(columns={c : c.replace(self.curr_branch + '.', '') for c in df.columns}, inplace=True)
            if self.k_flatten:
                df = df.reset_index()
            self.root_dataframes.append(df)

        

