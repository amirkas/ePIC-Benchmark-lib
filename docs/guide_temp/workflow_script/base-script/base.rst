Base ePIC Workflow Script
-------------------------

Below is the code for a simple workflow that:

* Retrieves and updates the ePIC Repository for each **Benchmark** with changes stated in its list of **DetectorConfig**.
* Compiles the ePIC Repository for each **Benchmark** and generates the material map if necessary.
* Simulates particle events and reconstructs particle trajectories with **npsim** and **eicrecon** for every **SimulationConfig** of every **BenchmarkConfig**.
* Generates plots and statistics for the tracking performance of every **Simulation** of every **Benchmark**. 
 
.. literalinclude:: ../../../../scripts/workflow_script.py
  :language: python
 
This code can also be found in the git repository at this :gitref:`location <scripts/workflow_script.py>`

.. note::

  * *The above workflow script wraps methods with python and bash apps so that users can customize the Parsl Executor used for each task as mentioned in .*

  * *stdout=AUTO_LOGNAME and stderr=AUTO_LOGNAME is used to generate log files for the workflow when debug=True in the Workflow's WorkflowConfig object*

  * *'generate_material_map' does nothing when generate_material_map=False for a given BenchmarkConfig*