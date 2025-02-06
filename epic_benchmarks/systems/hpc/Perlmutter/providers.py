from pydantic import field_validator, model_validator
from epic_benchmarks.parsl.providers import LocalProviderConfig, SlurmProviderConfig

class LocalProvider(LocalProviderConfig):

    pass

class SlurmProvider(SlurmProviderConfig):

    pass