import os
from dataclasses import dataclass, fields, field
from typing import Optional, List, Dict, Any

from epic_benchmarks.configurations import BaseConfig, ConfigKey
from epic_benchmarks.configurations.benchmark import BenchmarkConfig

@dataclass
class BenchmarkSuiteConfig(BaseConfig):

    save_filepath : Optional[str] = field(init=True, default=None)
    save_dir: Optional[str] = field(init=True, default=None)

    name: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="name",
        types=str,
        default="Benchmark_Suite",
        optional=True,
    ))
    benchmarks: ConfigKey = field(default_factory=lambda: ConfigKey(
        key_name="benchmarks",
        types=Optional[List[Dict[str, Any] | BenchmarkConfig]],
        optional=True,
        nested_config=BenchmarkConfig
    ))

    def add_benchmark(self):
        raise NotImplementedError()

    def save(self):

        if self.save_filepath is None:
            raise AttributeError("Must provide a location to save the configuration")
        path = self.save_filepath

        if self.save_dir:
            path = os.path.join(self.save_dir, path)
        dir = os.path.dirname(path)
        #Check if ancestor directory of filepath exists
        if not os.path.exists(dir):
            err = f"Directory {dir} does not exist. Create the parent directory of the file and try again."
            raise ValueError(err)
        #Check if user has write permissions at path
        if not os.access(path, os.W_OK):
            err = f"Path {path} is not writeable. Check file permissions at the path."
            raise ValueError(err)
        #Check if provided file extension is currently supported for configuration.
