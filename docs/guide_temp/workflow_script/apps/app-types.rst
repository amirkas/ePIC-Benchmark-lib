App Types
---------

A **Workflow Script** is defined with methods that are wrapped by 3 different types of apps:

* **bash_app** An app that executes a program normally executed on the command line. (npsim, eicrecon, echo, etc.)

* **python_app** An app that executes a python function. 

* **join_app** An app that returns the futures of multiple **bash_apps** and/or **python_apps**.