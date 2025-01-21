from parsl import bash_app
from epic_benchmarks.workflow.bash.methods import (
    pull_containers, clone_epic, checkout_epic_branch,
    compile_epic, run_npsim, run_eicrecon
)


pull_containers_app = bash_app(pull_containers)

clone_epic_app = bash_app(clone_epic)

checkout_epic_branch_app = bash_app(checkout_epic_branch)

compile_epic_app = bash_app(compile_epic)

run_npsim_app = bash_app(run_npsim)

run_eicrecon_app = bash_app(run_eicrecon)
