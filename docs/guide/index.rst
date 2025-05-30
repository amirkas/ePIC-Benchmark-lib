*****************
Creating a Workflow
*****************

Designing an **ePIC Workflow** involves the creation of two components:

* **The Workflow Configuration**

    * Determine the parameters of many different **simulations** / **reconstructions**. 

    * Design changes to the **ePIC detector geometry**.

    * **Partition** these simulations / reconstructions and ePIC detector geometry updates into seperate **Benchmarks**.

    * Choose how jobs get submitted and where they get submitted to (*Usually with a job scheduler on a HPC cluster*).

    * Choose which output files are kept in your filesystem

    * And more...

* **The Workflow Script**

    * Design and choose tasks that become part of your workflow

    * Create dependencies between tasks 

    * (*Optional*) Individually configure tasks to be handled by different job schedulers and execute with different computational resources. 

    * Choose which jobs get run inside a container 

    * And more...

This tutorial will guide you through the steps to create your own **Workflow Configuration**, **Workflow Script**,
and of course, how to execute your newly created **Workflow**. 

.. toctree::
   :maxdepth: 4
   :caption: Guide Contents:
   
   workflow_configuration/index
   workflow_script/index
   workflow_execution/run_workflow