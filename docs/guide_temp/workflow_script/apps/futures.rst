App Futures
-----------

A **Future** is an object returned by an asynchronous method, such as the afformentioned apps.
Attempting to obtain the result of **Future** object will block the **Workflow Script**
until the **app** associated with the future finishes execution.

Below is a demonstration of the afformentioned property. 

.. code-block:: python
   
    from ePIC_benchmarks.workflow.python import python_app

    @python_app
    def dummy_python_app_one():

        return None

    @python_app
    def dummy_python_app_two():

        return None

    #Get the future of the first python app
    dummy_future_one = dummy_python_app_one()

    #Block the script until dummy_python_app_one completes execution.
    #Print the result of dummy_python_app_one when it is ready. 
    print(dummy_future_one.result())

    #Get the future of the second python app
    dummy_future_two = dummy_python_app_two()