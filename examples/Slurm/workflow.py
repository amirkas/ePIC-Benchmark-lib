from typing import List
from epic_benchmarks.workflow import WorkflowConfig
from epic_benchmarks.parsl.types import FutureType

from epic_benchmarks.workflow.bash.apps.epic import clone_epic_app

def run(workflow_config : WorkflowConfig, all_futures : List[FutureType]):

    for benchmark_name in workflow_config.benchmark_names():

        clone_epic_future = clone_epic_app(workflow_config, benchmark_name)
        all_futures.append(clone_epic_future)




