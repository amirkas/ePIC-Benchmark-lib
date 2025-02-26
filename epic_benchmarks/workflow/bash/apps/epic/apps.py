from epic_benchmarks.workflow.bash import bash_app
from epic_benchmarks.workflow.bash.methods.epic import clone_epic, checkout_epic_branch, compile_epic, generate_material_map

clone_epic_app = bash_app(clone_epic)

checkout_epic_branch_app = bash_app(checkout_epic_branch)

compile_epic_app = bash_app(compile_epic)

generate_material_map = bash_app(generate_material_map)