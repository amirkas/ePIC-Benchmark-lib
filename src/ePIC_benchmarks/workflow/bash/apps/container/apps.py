from ePIC_benchmarks.workflow.bash import bash_app
from ePIC_benchmarks.workflow.bash.methods.container import pull_containers


pull_containers_app = bash_app(pull_containers)