BenchmarkConfig
---------------

The BenchmarkConfig allows for Workflows to be partitioned in such a way that:

* Each BenchmarkConfig uses a single ePIC repository.
* Updates to detector geometry description files from every child DetectorConfig object are made to the single ePIC repository.
* All **npsim** and **eicrecon** executions defined by the child SimulationConfig objects use the same, updated ePIC repository. 

The BenchmarkConfig object has the following **required attributes**:

* **name** - Unique name of the Benchmark
* **simulation_configs** - List of **SimulationConfig** objects.
* **detector_configs** - List of **DetectorConfig** objects.

The BenchmarkConfig object has the following **optional attributes**:

* **epic_branch** - The branch of the ePIC git repository to checkout. (**Default: "main"**)
* **existing_epic_directory_path** - Path to an already existing ePIC repository to be used. (**Default: None**)
* **generate_material_map** - Toggles whether the material map can be generated in the Workflow Script. (**Default: False**)
* **existing_material_map_path** - Path to an already generated material map to be used. (**Default: None**)
* **benchmark_dir_name** - The name for the Benchmark directory in the Workflow Directory. (**Default: The current BenchmarkConfig's 'name' attribute**)
* **simulation_out_directory_name** - The name for the Benchmark directory's subdirectory that stores output files of **npsim** executions (**Default: "simulations"**)
* **reconstruction_out_directory_name** - The name for the Benchmark directory's subdirectory that stores output files of **eicrecon** executions (**Default: "reconstructions"**)
* **analysis_out_directory_name** - The name for the Benchmark directory's subdirectory that stores output files of **Analysis** routines (**Default: "analysis"**) 


Below is an example of a **BenchmarkConfig** with a single **SimulationConfig** object and a single **DetectorConfig** object
previously defined in this document in their respective sections.

.. literalinclude:: ../../../example_configs/benchmark_config_ex.py
  :language: python