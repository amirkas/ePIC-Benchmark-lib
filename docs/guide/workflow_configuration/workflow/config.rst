

WorkflowConfig
--------------


The **WorkflowConfig** object is the root configuration object of a Workflow, which uses a single **ParslConfig** object to
define the task execution pattern for all tasks of every Benchmark defined by a **BenchmarkConfig**. 

Required Attributes
^^^^^^^^^^^^^^^^^^^

The required attribues of a **WorkflowConfig** object are as follows:

* **name** - The name of the Workflow

* **benchmarks** - A list of **BenchmarkConfig** instances.

* **parsl_config** - A **ParslConfig** instance. 

Optional Attributes
^^^^^^^^^^^^^^^^^^^

The optional attribues of a **WorkflowConfig** object are as follows:

* **debug** - Toggles debugging mode for the Workflow (**Default: False**)

* **working_directory** - The parent directory of the Workflow Directory. (**Default: The current working directory**)

* **redo_all_benchmarks** - Toggles whether all tasks are redone upon re-execution of the Workflow or if only incomplete tasks from a previous workflow are completed. (**Default: False**)

* **redo_epic_building** - Toggles whether the ePIC repository is to be re-cloned and re-built. (**Default: False**)

* **redo_simulations** - Toggles whether all **npsim** executions are to be redone. 

* **redo_reconstructions** - Toggles whether all **eicrecon** executions are to be redone. 

* **redo_analysis** - Toggles whether all **analysis** routines are to be redone. 

* **keep_epic_repos** - Toggles whether each **Benchmark's** ePIC repository is kept after a Workflow is completed.

* **keep_simulation_outputs** - Toggles whether the output files of all **npsim** executions are kept after a Workflow is completed. 

* **keep_reconstruction_outputs** - Toggles whether the output files of all **eicrecon** executions are kept after a Workflow is completed. 

* **keep_analysis_outputs** - Toggles whether the output files of all **analysis** routines are kept after a Workflow is completed. 


Example WorkflowConfig
^^^^^^^^^^^^^^^^^^^^^^

The following is an example of a **WorkflowConfig** object using a single **BenchmarkConfig** instance
and the **ParslConfig** instance already defined previously in their respective sections. 

.. literalinclude:: example_configs/workflow_config_ex.py
  :language: python