Creating your own apps
----------------------

Asides from using apps and workflow scripts already provided from this package,
this package supports the use of custom apps that meet certain requirements.

Creating apps in this package is identical to creating apps when using **Parsl** by itself.
Rather than repeating an already excellent guide on creating apps,
we suggest you read **Parsl's** documention on '`Creating Apps <https://parsl.readthedocs.io/en/stable/userguide/apps/index.html>`_ ' 

We also provide additional tools to help you develop your own bash_apps.

Concatenating multiple commands for a single Bash App
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Many bash apps may require the sequential execution of several CLI programs.
There are two methods for implementing a bash app with this feature.


1. Use the **concatenate_commands** function, provided in **ePIC_benchmarks.workflow.bash.utils** (**Recommended**)
   
   **Pros:**

   * Simplifies the code for multi-program bash_apps.

   * * All programs are able to run within the same instance of a container.

   **Cons:**

   * Cannot specify individual task-dependent parameters for each program.

   * Debugging logs are more verbose for a single bash_app and make it more difficult to identify a problem program.

   * Programs cannot be run concurrently, only sequentially. 

   **Example:**

   .. code-block:: python

        from ePIC_benchmarks.workflow.bash import bash_app
        from ePIC_benchmarks.workflow.bash.utils import concatenate_commands

        @bash_app(...)
        def multiple_program_bash_app(...):

            program_one_command : str = ...
            program_two_command : str = ...
            program_three_command : str = ...

            all_commands = concatenate_commands(
                program_one_command, program_two_command, program_three_command
            )
            return all_commands

2. Convert your **bash_app** into a **join_app** where each of its internal **bash_apps** has the responsibility of a **single CLI program**
   
   **Pros:**

   * Seperation of bash_apps allows for clear identification of failed tasks when debugging

   * Allows for each CLI program to have their own **ParslExecutor** and other definable task-dependent parameters.

   * Programs can be run concurrently (*In this case, it may be more suitable to have these programs executed in the higher-level workflow script rather than within a join_app*)
   
   **Cons:**

   * Introduces more complexity to your code

   * Executing each **ClI program** in a container with the same image requires reinitialization of the container for each program. 

   **Example:**

   .. code-block:: python

        from ePIC_benchmarks.workflow.bash import bash_app
        from ePIC_benchmarks.workflow.join import join_app

        @bash_app(...)
        def cli_program_one(...):
            return "echo 'executing program one'"

        @bash_app(...)
        def cli_program_two(...):
            return "echo 'executing program two'"

        @bash_app(...)
        def cli_program_three(...):
            return "echo 'executing program two'"

        @join_app(...)
        def joined_bash_app(...):

            program_one_future = cli_program_one(...)
            program_two_future = cli_program_two(..., dependency=program_one_future)
            program_three_future = cli_program_three(..., dependency=program_two_future)
            return program_three_future

Containerizing your Bash App
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To support the execution of **bash_apps** within containers, we suggest you use the following template (*Using a shifter Container as an example*):

.. code-block:: python

    from ePIC_benchmarks.workflow.bash import bash_app
    from ePIC_benchmarks.container._base import BaseContainerConfig

    @bash_app
    def example_bash_app(*args, container : BaseContainerConfig = None, kwargs**):

        #Get the string representation of the CLI command(s) for your bash app
        example_bash_cmd = ...
        if container is not None:
            example_bash_cmd = container.init_with_extra_commands(example_bash_cmd)
        return example_bash_cmd