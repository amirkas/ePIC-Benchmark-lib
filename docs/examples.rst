********
Examples
********

Perlmutter
==========

Headless Workflow Submission (RECOMMENDED)
------------------------------------------

In most cases, it is preferable to submit a Workflow to Slurm that will execute
on a computational resource independent of a Login Node. This avoids early termination
of your workflow in the scenario that your Perlmutter Login Node session is terminated,
which can occur for many reasons. 

In this case the strategy for workflow submission is to:

1. Save the Workflow Configuration and Workflow Script to seperate files.

2. Submit a job to the Slurm Scheduler that executes a package-provided python script from the Command Line that:

   a. Loads the Workflow Configuration and Workflow Script from files, found using user-provided file paths.

   b. Handles individual task execution locally, in the perspective of the cluster of acquired Compute Nodes.

The following code acts as a template for this Workflow Submission Strategy:

Python script that creates the Workflow Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file can be :gitref:`found here <examples/Perlmutter/Headless_Workflow/create_config.py>`

.. literalinclude:: ../examples/Perlmutter/Headless_Workflow/create_config.py
  :language: python

Slurm Submission Script 
^^^^^^^^^^^^^^^^^^^^^^^^

This file can be :gitref:`found here <examples/Perlmutter/Headless_Workflow/submit_headless_workflow.sl>`

.. literalinclude:: ../examples/Perlmutter/Headless_Workflow/submit_headless_workflow.sl
  :language: bash


Local Workflow Job Submissions
------------------------------

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


**Note:** Unfortunately, this strategy is prone to early-termination in the scenario that your
continually running python script or your Login Node terminates before the workflow is complete.
Therefore, we **highly recommend** using the previously mentioned **Headless Workflow Submission** strategy to complete your workflows.





