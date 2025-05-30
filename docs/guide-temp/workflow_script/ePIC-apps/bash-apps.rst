ePIC Workflow Bash Apps
-----------------------

This package has the following bash apps already defined for your use. 

Container-related Apps
^^^^^^^^^^^^^^^^^^^^^^

* **pull_containers_app** - Pull a container to be ready for initialization.

ePIC repository-related Apps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **clone_epic_app** - Clone the ePIC repository into the directory of a Benchmark.

* **checkout_epic_branch_app** - Switch the ePIC repository of a Benchmark to the branch defined in its associated **BenchmarkConfig**.

* **compile_epic_app** - Compile the ePIC repository of a Benchmark.

* **generate_material_map_app** - Generate the material map for the ePIC Repository of a Benchmark.

Simulation-related Apps
^^^^^^^^^^^^^^^^^^^^^^^

* **run_npsim_app** - Execute npsim with the parameters defined in a specified **SimulationConfig** of a specified **BenchmarkConfig**.

* **run_eicrecon_app** - Execute eicrecon with the parameters defined in a specified **SimulationConfig** of a specified **BenchmarkConfig**.