===================
Parsl Configuration
===================

ParslConfig
-----------

The **ParslConfig** object is used to define how and where tasks are executed during the duration of the Workflow execution. 
**ParslConfig** as well as every **ParslExecutorConfig**, **ParslProviderConfig**, and **ParslLauncherConfig** exactly matches the classes defined in
the **Parsl** package, a third-party package for Scientific Computing with documentation that can be found `here <https://parsl.readthedocs.io/en/stable/index.html>`_ .

When defining your **ParslConfig** object, we highly recommend following the
section in **Parsl's** documentation titled `Configuring Parsl <https://parsl.readthedocs.io/en/stable/userguide/configuration/index.html>`_ .
This package handles loading of the **ParslConfig** for you, but you must define the **ParslConfig** itself.

.. note::
    *This Package does not support the use of instances of Parsl's classes, but rather wrapped versions of these classes with the same name*
    *and the prefix* **'Config'**. *This is with the exception of the root Parsl Config which is has the name* **'ParslConfig'**.

.. literalinclude:: example_configs/parsl_config_ex.py
  :language: python

For examples of **ParslConfig's** that may match your desired execution pattern on your specific computing infrastructure, see :ref:`the example section <examples-sec>`. 
