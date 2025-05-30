
Running your Workflow
=====================

With your **Workflow Configuration** and **Workflow Script** now defined, you may be wondering how to actually run your workflow.
To do so, this package provides two alternative methods for use in different scenarios. 

Starting your workflow from the Command Line
---------------------------------------------

In many cases, it may be useful to start your workflow by invoking a command on your system's command line interface.
To do so, this package can be called as a script and does the following:

1. Create a **WorkflowConfig** instance by reading a saved **Workflow Configuration file**.
2. Import the **Workflow's encapsulating function** from a **Workflow Script** python file.

To do this, use the following command:

.. code-block:: bash

    python -m ePIC_benchmarks "{config_path}"  --script="{script_path}" --funcName="{workflow_function_name}"

For clarity the arguments correspond to:

* *config_path* - The relative or absolute path to a saved Workflow Configuration file.
* *script_path* (Optional) - The relative or absolute path to a saved Workflow Script python file. (**Default:** 'workflow_script.py')
* *funcName* (Optional) - the name of the function encapsulting the workflow in the Workflow Script file (**Default:** 'run')

Starting your workflow from a python script
--------------------------------------------

Rather than saving your **WorkflowConfig** to your file system, or defining your **Workflow Script** in a seperate file,
it may be easier to have both of these components directly accessible as python objects within a python script.
Executing a workflow now becomes a simpler matter of calling a package-provided function with these python objects as inputs.

The function to do exactly this is called **execute_workflow** and is found under the module: **ePIC_benchmarks.workflow.run**.

The following is pseudocode showing how you can execute your workflow within a python script:

.. code-block:: python

    from ePIC_benchmarks.workflow import WorkflowConfig
    from ePIC_benchmarks.workflow.bash import bash_app
    from ePIC_benchmarks.workflow.python import python_app
    from ePIC_benchmarks.workflow.run import execute_workflow

    #Placeholder for a WorkflowConfig instance
    EXAMPLE_WORKFLOW_CONFIG = WorkflowConfig(...)

    #Placeholder for user defined bash app
    @bash_app(...)
    def example_bash_app(...):
        bash_command : str = ...
        return bash_command

    #Placeholder for user defined python app
    @python_app(...)
    def example_python_app(...):
        return ...

    #Placeholder for a Worklow's encapsulating function
    def run(...):

        bash_app_future = example_bash_app(...)
        python_app_future = example_python_app(..., dependency=bash_app_future)
        return python_app_future

    #Execute the workflow
    execute_workflow(
        workflow=EXAMPLE_WORKFLOW_CONFIG,
        script_func=run
    )
    