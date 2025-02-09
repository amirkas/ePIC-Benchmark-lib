from epic_benchmarks.workflow.bash import bash_app
from epic_benchmarks.workflow.bash.methods.simulation import run_npsim, run_eicrecon

run_npsim_app = bash_app(run_npsim)

run_eicrecon_app = bash_app(run_eicrecon)