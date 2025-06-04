The structure of a Workflow Script
----------------------------------

When creating a **Workflow Script**, it is important to:

* State the tasks to be executed and their dependencies **inside a function**.

* **Return a list of futures** of all of the apps that are **not dependencies of other apps**.

On the backend, this package wraps the workflow function as a join_app.
To ensure all tasks get executed, the package must have access to all of the final futures of each task dependency chain.

The following is pseudocode showing the required structure of a **Workflow Script**:

.. code-block:: python

    from ePIC_benchmarks.workflow import WorkflowConfig
    from ePIC_benchmarks.workflow.bash import bash_app     
    from ePIC_benchmarks.workflow.python import python_app

    @bash_app
    def example_bash_app(config : WorkflowConfig, other_args, kwargs**):

        #Return the string representation of the command ordinally executed on the Command Line

    @python_app
    def example_python_app(config : WorkflowConfig, other_args, kwargs**):

        #Return the desired output of this python app.

    @bash_app
    def example_another_bash_app(config : WorkflowConfig, other_args, kwargs**):

        #Return the string representation of the command ordinally executed on the Command Line


    #The tasks to be executed must be enclosed inside a function ('usually named run')
    #with a WorkflowConfig as the type of its sole input argument.
    def run(config : WorkflowConfig):

        #Initialize a list to store the futures of the last tasks to be completed.
        final_futures = []

        #Retrieve the future of previously defined bash app which is called.
        example_bash_app_future = example_bash_app(config, ...)

        #Retrieve the future of previously defined python app
        #which is called only when its dependency ('example_bash_app') has been completed. 
        example_python_app_future = example_python_app(config, ..., dependency=example_bash_app_future)

        for some_value of some_iterable:

            #Retrieve the future of previously defined bash app
            #which is called only when its dependency ('example_python_app') has been completed. 
            example_another_bash_app_future = example_another_bash_app(config, some_value, ..., dependency=example_python_app_future)
            
            #Since there are no more tasks dependent on this task, add this task's future to the 'final_futures' list.
            final_futures.append(example_another_bash_app_future)

        #Return the futures associated with apps that are not dependencies of other apps.
        return final_futures