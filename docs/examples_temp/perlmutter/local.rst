******************************
Local Workflow Job Submissions
******************************

This submission strategy involves running a python script for the duration of the workflow on your current Login Node.
The **ParslConfig** associated with this stategy allows for this package to interact with the Slurm Scheduler directly,
without the need for you to explicity submit your jobs to Slurm. 

In this case the strategy for workflow submission is to:

1. Create the Workflow Configuration and Workflow Script (Which can be created in the same file or seperate files)

2. Run a python script that calls a package-provided python function with the following inputs:

   * A WorkflowConfig instance (*which can be created in the same python script or loaded from a configuration file*)

   * Either:

     * A path to a Workflow Script file + the name of the Workflow's encapsulating function

     * The workflow's encapsulating function itself.

The following code acts as a template for this Workflow Submission Strategy (*Using a Workflow Script saved as a seperate file to the submission python script*).

Python script that creates the Workflow Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file can be :gitref:`found here <examples/Perlmutter/Local_Slurm_Submission_Workflow/create_config.py>`

.. literalinclude:: ../examples/Perlmutter/Local_Slurm_Submission_Workflow/create_config.py
  :language: python

Python Submission Script 
^^^^^^^^^^^^^^^^^^^^^^^^

This file can be :gitref:`found here <examples/Perlmutter/Local_Slurm_Submission_Workflow/submit_tasks_script.py>`

.. literalinclude:: ../examples/Perlmutter/Local_Slurm_Submission_Workflow/submit_tasks_script.py
  :language: python


.. warning::
  Unfortunately, this strategy is prone to early-termination in the scenario that your
  continually running python script or your Login Node terminates before the workflow is complete.
  Therefore, we **highly recommend** using the previously mentioned **Headless Workflow Submission** strategy to complete your workflows.