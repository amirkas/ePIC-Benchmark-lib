from epic_benchmarks.workflow.bash import containerized_bash_app
from epic_benchmarks.workflow.bash.methods.container import pull_containers


pull_containers_app = containerized_bash_app(pull_containers)