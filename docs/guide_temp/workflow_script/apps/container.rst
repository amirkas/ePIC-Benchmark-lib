ContainerConfig
---------------

Certain apps may need to be executed within a container.
The ContainerConfig object is designed to enable this.

Currently, this package supports the use of the following Containers:

* **Docker** - Config named **DockerConfig**
* **Shifter** - Config named **ShifterConfig**

The afformentioned apps provided by this package support containerization via the container keyword argument.

A ContainerConfig object is initialized with the following required keyword arguments:

* **image** - Image of the container to be used. 

and the following optional keyword arguments:

* **entry_point** - Location of an entry point script used when initializing the container.