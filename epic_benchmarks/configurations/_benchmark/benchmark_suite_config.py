import yaml
import os
from pathlib import Path
from .benchmark_config import BenchmarkConfig

CWD = os.getcwd()
NAME_KEY = "name"
BENCHMARK_SUITE_NAME_KEY = "benchmark_suite_name"
BENCHMARK_LIST_KEY = "benchmarks"

class BenchmarkSuiteConfig:

    def __init__(self, file_path : str, file_dir="", load_suite=None, name="BenchmarkSuite", benchmarks_list = [], auto_save=False, overwrite = True):

        
        if file_dir == None:
            self.file_path = file_path
        elif len(file_dir) != 0:
            self.file_path = os.path.join(file_dir, file_path)
        else:
            self.file_path = os.path.join(CWD, file_path)

        #If loading from dictionary, load it and don't read from a file or create a new one.
        if load_suite != None:
            if not isinstance(load_suite, dict):
                raise Exception("Benchmark Suite to load must be a dict")
            config = load_suite
            self.auto_save = auto_save
            self.overwrite = overwrite
            for key, value in config.items():
                if key == BENCHMARK_LIST_KEY:
                    benchmarks = []
                    for benchmark_dict in config[key]:
                        benchmarks.append(BenchmarkConfig(load_benchmark_config=benchmark_dict))
                    setattr(self, key, benchmarks)
                if key == BENCHMARK_SUITE_NAME_KEY:
                    setattr(self, key, value)
            

        #If file already exists, load the file
        elif os.path.exists(self.file_path):
            
            self.auto_save = auto_save
            self.overwrite = overwrite
            if self.overwrite:
                setattr(self, BENCHMARK_SUITE_NAME_KEY, name)
                for benchmark in benchmarks_list:
                    if not isinstance(benchmark, BenchmarkConfig):
                        raise Exception("Benchmarks must be an instance of the BenchmarkConfig class")
                setattr(self, BENCHMARK_LIST_KEY, benchmarks_list[:])
                if self.auto_save:
                    self.save()
                return
            else:
                with open(self.file_path, 'r') as f:
                    config = yaml.safe_load(f)
                for key, value in config.items():
                    if key == BENCHMARK_LIST_KEY:
                        benchmarks = []
                        for benchmark_dict in config[key]:
                            benchmark = BenchmarkConfig(load_benchmark_config=benchmark_dict)
                            benchmarks.append(benchmark)
                        setattr(self, key, benchmarks)
                    if key == BENCHMARK_SUITE_NAME_KEY:
                        setattr(self, key, value)

        #If file doesn't exist, create a new file at the specified path
        else:

            setattr(self, BENCHMARK_SUITE_NAME_KEY, name)
            self.auto_save = auto_save
            self.overwrite = overwrite

            for benchmark in benchmarks_list:
                if not isinstance(benchmark, BenchmarkConfig):
                    raise Exception("Benchmarks must be an instance of the BenchmarkConfig class")
            setattr(self, BENCHMARK_LIST_KEY, benchmarks_list[:])
            if self.auto_save:
                self.save()
            

    def add_benchmark(self, benchmark):

        if not isinstance(benchmark, BenchmarkConfig):
            print("benchmark must have type: BenchmarkConfig")
            return
        benchmarks = getattr(self, BENCHMARK_LIST_KEY)[:]
        benchmarks.append(benchmark)
        setattr(self, BENCHMARK_LIST_KEY, benchmarks)
        if self.auto_save:
            self.save()


    def get_benchmark(self, benchmark_name : str):
        benchmarks = getattr(self, BENCHMARK_LIST_KEY)[:]
        for benchmark in benchmarks:
            if benchmark_name == getattr(benchmark, NAME_KEY):
                return benchmark
        raise Exception("Could not find a benchmark with that name")
    
    def get_benchmark_branch(self, benchmark_name : str):
        benchmark = self.get_benchmark(benchmark_name=benchmark_name)
        return benchmark.get_branch()
    
    def get_benchmark_detector_configs(self, benchmark_name : str):
        benchmark = self.get_benchmark(benchmark_name=benchmark_name)
        return benchmark.get_detector_configs()

    def get_benchmark_common_sim(self, benchmark_name : str):
        benchmark = self.get_benchmark(benchmark_name=benchmark_name)
        return benchmark.get_common_simulation_config()

    def get_benchmark_simulation(self, benchmark_name : str, simulation_name : str):
        benchmark = self.get_benchmark(benchmark_name=benchmark_name)
        return benchmark.get_simulation_config(simulation_name)
    
    def get_benchmark_suite_name(self):
        return getattr(self, BENCHMARK_SUITE_NAME_KEY)

    def get_benchmark_names(self):
        names = []
        benchmarks = getattr(self, BENCHMARK_LIST_KEY)[:]
        for benchmark in benchmarks:
            names.append(getattr(benchmark, NAME_KEY))
        return names

    def get_simulation_names(self, benchmark_name):
        benchmark = self.get_benchmark(benchmark_name=benchmark_name)
        return benchmark.get_simulation_names()

    def get_config_dict(self):
        benchmarks = getattr(self, BENCHMARK_LIST_KEY)[:]
        config = {}
        config[BENCHMARK_SUITE_NAME_KEY] = getattr(self, BENCHMARK_SUITE_NAME_KEY)
        config[BENCHMARK_LIST_KEY] = [benchmark.get_config_dict() for benchmark in benchmarks]
        return config

    def save(self):

        config_dict = self.get_config_dict()
        
        with open(self.file_path, "w") as f:
            yaml.safe_dump(config_dict, f, default_flow_style=False)

    def reset_config(self):
        setattr(self, BENCHMARK_LIST_KEY, [])
        with open(self.file_path, "w") as f:
            yaml.safe_dump({}, f, default_flow_style=False)
        
        