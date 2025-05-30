******************************************
Headless Workflow Submission (RECOMMENDED)
******************************************

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