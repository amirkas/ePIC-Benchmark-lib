# from .executor import WorkflowExecutor
# from .manager import ParslWorkflowManager
# from .parsl_configs import SlurmProviderConfig, HeadlessConfig
from epic_benchmarks.workflow.containers import Shifter, Docker

EPIC_REPO_URL = "https://github.com/eic/epic.git"

CONTAINER_MAP = {
    "shifter" : Shifter(),
    "docker" : Docker()
}

SUPPORTED_CONTAINERS = CONTAINER_MAP.keys()