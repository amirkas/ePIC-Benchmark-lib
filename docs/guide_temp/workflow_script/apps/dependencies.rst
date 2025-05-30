Creating Task Dependencies
--------------------------

The above code also demonstrates one method of creating a dependency of one app to another for sequential workflows.
The following code shows an example of creating dependencies in both parallel and sequential workflows.

.. code-block:: python 

    import random
    from ePIC_benchmarks.workflow.bash import bash_app
    from ePIC_benchmarks.workflow.python import python_app

    @bash_app
    def echo_starting(kwargs**):

        return "echo 'Starting!'"

    @python_app
    def return_one(kwargs**):

        return 1

    @python_app
    def add_random(number, kwargs**):

        return number + random.random()

    @bash_app
    def echo_done(kwargs**):

        return "echo 'Starting!'"

    echo_starting_future = echo_done()

    #return_one App invocation dependent on echo_starting completion.
    return_one_future = return_one(dependency=echo_starting_future)

    add_random_future_list = []

    for i in range(10):

        #add_random App invocation dependent on return_one completion.
        #This means all add_random calls can be potentially be executed concurrently.
        add_random_future = add_random(dependency=return_one_future)

        #Store all add_random futures in list
        add_random_future_list.append(add_random_future)

    #echo_done App invocation dependent on the completion of all add_random invocations.
    echo_done_future = echo_done(dependencies=add_random_future_list)

.. note::
    *The name of the keyword argument to add a dependency does not matter.*
    *However, 'kwargs***' *must be added to the app signature.*