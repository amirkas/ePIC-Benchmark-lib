from epic_benchmarks.workflow.bash import containerized_bash_app
from epic_benchmarks.workflow.bash.methods.epic import clone_epic, checkout_epic_branch, compile_epic

clone_epic_app = containerized_bash_app(clone_epic)

checkout_epic_branch_app = containerized_bash_app(checkout_epic_branch)

compile_epic_app = containerized_bash_app(compile_epic)