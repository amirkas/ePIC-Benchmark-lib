********
Tutorial
********


Workflow Configuration
^^^^^^^^^^^^^^^^^^^^^^

The Structure of a Workflow Configuration
-----------------------------------------

The configuration for a workflow has the following structure of nested config objects.

* WorkflowConfig

    * ParslConfig

        * ParslExecutorConfig

            * ParslProviderConfig

                * ParslLauncherConfig
  
    * BenchmarkConfig(s)

        * SimulationConfig(s)
        * DetectorConfig(s)



SimulationConfig
----------------

The SimulationConfig object is used to define the parameters passed into **npsim** and **eicrecon** executions.

The following are **required attributes** to be defined for a SimulationConfig:

* **num_events** - Number of events to be simulated
* **momentum** or **momentum_min** + **momentum_max** - Single momentum or Range of momenta of simulated particles.
* **detector_xml** - Path of the detector description xml file to be simulated, with reference to the ePIC build directory.
* **distribution_type** - Phase space distribution of simulated particles. 
* **theta_min** or **eta_min** - Minimum range of the chosen phase space distribution defined by **distribution_type**.
* **theta_max** or **eta_max** - Maximum range of the chosen phase space distribution defined by **distribution_type**.

The following are **optional attributes** to be defined for a SimulationConfig:

* **particle** - The particle to be simulated. (**Default: PionPlus**)
* **multiplicity** - The multiplicity of simulated particle events. (**Default: 1.0**)
* **use_material_map** - Toggles whether the material map given in the parent BenchmarkConfig is used for the simulation. (**Default: False**)
* **enable_gun** - Toggles whether the particle gun is enabled. (**Default: True**)

.. code-block:: python

    from ePIC_benchmarks.simulation import SimulationConfig
    from ePIC_benchmarks.simulation.simulation_types import GunDistribution, Particle

    EXAMPLE_SIMULATION_CONFIG = SimulationConfig(
        num_events=10000,
        momentum="10GeV",
        distribution_type=GunDistribution.Eta,
        eta_min=-4,
        eta_max=4,
        particle=Particle.PionPlus,
        detector_xml="epic_craterlake_tracking_only.xml"
    )

DetectorConfig
--------------

The **DetectorConfig** object is used to dynamically alter the ePIC detector geometry before its compilation. 

The following are the required attributes of the **DetectorConfig** object:

* **file** - The relative path of the detector geometry description XML file to be updated with respect to the ePIC repository's **compact** directory. 
* **edit_element_trees** - An **XmlElement** tree or list of **XmlElement** Trees used to search for XML elements and define how they're updated. 

Each detector geometry file in the ePIC repository has a tree-like structure of XML elements with different tags and attributes.
Making changes to an XML element requires that a query be constructed to find the XML element of interest.
This library manages query construction for you, but you must define the XML Element tree associated with the query.
This is done with the use of **XmlElement** objects defined in the submodules of **ePIC_benchmarks.detector.xml_elements** to construct an **XmlElement** Tree. 

The list and hierarchical structure of available XML elements for use for each submodule are as follows:

**xml_elements.detector**

* XmlDetectorElement

  * XmlModuleElement

    * XmlModuleComponentElement

    * XmlTrdElement

    * XmlFrameElement

  * XmlLayerElement

    * XmlLayerMaterialElement

    * XmlRphiLayoutElement

    * XmlBarrelEnvelopeElement

    * XmlZLayoutElement

    * XmlEnvelopeElement

    * XmlRingElement

  * XmlDimensionsElement

  * XmlTypeFlagsElement

**xml_elements.constant**

* XmlConstantElement

**xml_elements.plugins**

* XmlArgumentElement

* XmlPluginElement

**xml_elements.readout**

* XmlReadoutElement

  * XmlSegmentationElement

* XmlReadoutIdElement

To construct a query such that for **every XmlModuleComponentElement**
of **every XmlModuleElement** of **every XmlDetectorElement**, the **XmlModuleComponentElement's** **'sensitive'** attribute is updated to be **false**,
we would define the following **XmlElement** tree:

.. code-block:: python

    XmlDetectorElement(
        modules=XmlModuleElement(
            module_components=XmlModuleComponentElement(
                update_attribute="sensitive",
                update_value="false",
                update_type='SET'
            )
        )
    )

Whereas to construct a query where the **'sensitive'** attribute of 
the **XmlModuleComponentElement** with **material="Silicon"** belonging to
the **XmlModuleElement** with **name="Module1"** belonging to
the **XmlDetectorElement** with **name="InnterTrackerEndcapP"** is updated to be **false**,
we would define the following **XmlElement** tree:

.. code-block:: python

    XmlDetectorElement(
        name="InnerTrackerEndcapP",
        modules=XmlModuleElement(
            name="Module1",
            module_components=XmlModuleComponentElement(
                material="Silicon",
                update_attribute="sensitive",
                update_value="false",
                update_type='SET'
            )
        )
    )

**Note:** All of the leaf nodes of an **XmlElement** tree must have non-None values for its **update_type** and the **update_attribute** parameters.

To integrate this example of an detector geometry update into a workflow for the **tracking/silicon_disks.xml** detector description file,
we would initialize the following DetectorConfig object:

.. code-block:: python

    from ePIC_benchmarks.detector import DetectorConfig
    from ePIC_benchmarks.detector.xml_elements.detector import (
        XmlDetectorElement, XmlModuleElement, XmlModuleComponentElement
    )

    EXAMPLE_DETECTOR_CONFIG = DetectorConfig(
        file="tracking/silicon_disks.xml",
        edit_element_trees=XmlDetectorElement(
            name="InnerTrackerEndcapP",
            modules=XmlModuleElement(
                name="Module1",
                module_components=XmlModuleComponentElement(
                    material="Silicon",
                    update_attribute="sensitive",
                    update_value="false",
                    update_type='SET'
                )
            )
        )
    )

The value of an XML element's **'update_type'** defines the way that an XML Element attribute is updated.
The value of an XML element's **'update_attribute'** states the attribute that should be updated.
The value of an XML element's **'update_value'** states the value that the attribute given in **'update_attribute'** should be updated with.

The currently allowed **update_types** are as follows:

* **SET** - Set the value of the attribute given in **'update_attribute'** to the the value given in **'update_value'**.
* **ADD** - Add the value given in **'update_value'** to the already existing value of the attribute given in **'update_attribute'**.
* **DELETE** - Delete the attribute given in **'update_attribute'** from the Xml Element. 


BenchmarkConfig
---------------

The BenchmarkConfig allows for Workflows to be partitioned in such a way that:

* Each BenchmarkConfig uses a single ePIC repository.
* Updates to detector geometry description files from every child DetectorConfig object are made to the single ePIC repository.
* All **npsim** and **eicrecon** executions defined by the child SimulationConfig objects use the same, updated ePIC repository. 

The BenchmarkConfig object has the following **required attributes**:

* **name** - Unique name of the Benchmark
* **simulation_configs** - List of **SimulationConfig** objects.
* **detector_configs** - List of **DetectorConfig** objects.

The BenchmarkConfig object has the following **optional attributes**:

* **epic_branch** - The branch of the ePIC git repository to checkout. (**Default: "main"**)
* **existing_epic_directory_path** - Path to an already existing ePIC repository to be used. (**Default: None**)
* **generate_material_map** - Toggles whether the material map can be generated in the Workflow Script. (**Default: False**)
* **existing_material_map_path** - Path to an already generated material map to be used. (**Default: None**)
* **benchmark_dir_name** - The name for the Benchmark directory in the Workflow Directory. (**Default: The current BenchmarkConfig's 'name' attribute**)
* **simulation_out_directory_name** - The name for the Benchmark directory's subdirectory that stores output files of **npsim** executions (**Default: "simulations"**)
* **reconstruction_out_directory_name** - The name for the Benchmark directory's subdirectory that stores output files of **eicrecon** executions (**Default: "reconstructions"**)
* **analysis_out_directory_name** - The name for the Benchmark directory's subdirectory that stores output files of **Analysis** routines (**Default: "analysis"**) 


Below is an example of a **BenchmarkConfig** with a single **SimulationConfig** object and a single **DetectorConfig** object
previously defined in this document in their respective sections.

.. code-block:: python

    from ePIC_benchmarks.benchmark import BenchmarkConfig

    EXAMPLE_BENCHMARK_CONFIG = BenchmarkConfig(
        simulation_configs=[EXAMPLE_SIMULATION_CONFIG],
        detector_configs=[EXAMPLE_DETECTOR_CONFIG],
        epic_branch="main",
        generate_material_map=False
    )

ParslConfig
-----------

The **ParslConfig** object is used to define how and where tasks are executed during the duration of the Workflow execution. 
**ParslConfig** as well as every **ParslExecutorConfig**, **ParslProviderConfig**, and **ParslLauncherConfig** exactly matches the classes defined in
the **Parsl** package, a third-party package for Scientific Computing with documentation that can be found `here <https://parsl.readthedocs.io/en/stable/index.html>`_ .

When defining your **ParslConfig** object, we highly recommend following the
section in **Parsl's** documentation titled `Configuring Parsl <https://parsl.readthedocs.io/en/stable/userguide/configuration/index.html>`_ .
This package handles loading of the **ParslConfig** for you, but you must define the **ParslConfig** itself.

.. code-block:: python

    from ePIC_benchmarks.parsl.config import ParslConfig
    from ePIC_benchmarks.parsl.executors import HighThroughputExecutorConfig
    from ePIC_benchmarks.parsl.providers import LocalProviderConfig
    from ePIC_benchmarks.parsl.launchers import SrunLauncherConfig

    EXAMPLE_PARSL_CONFIG = ParslConfig(
        executors=[
            HighThroughputExecutorConfig(
                label="HTEC_Executor",
                cores_per_worker=2,
                max_workers_per_node=10,
                provider=LocalProviderConfig(
                    nodes_per_block = 1,
                    launcher=SrunLauncherConfig(overrides='-c 20'),
                    max_blocks=1,
                    init_blocks=1,
                ),
            ),
        ],
    )

For examples of **ParslConfig's** that may match your desired execution pattern on your specific computing infrastructure, see '...'. 

WorkflowConfig
--------------

The **WorkflowConfig** object is the root configuration object of a Workflow, which uses a single **ParslConfig** object to
define the task execution pattern for all tasks of every Benchmark defined by a **BenchmarkConfig**. 

The **WorkflowConfig** object also acts as an API for the execution of certain routines, and retrieval of paths of files generated by a Workflow.
More information on the API component of the **WorkflowConfig** can be found in the following sections:

...

The required attribues of a **WorkflowConfig** object are as follows:

* **name** - The name of the Workflow

* **benchmarks** - A list of **BenchmarkConfig** instances.

* **parsl_config** - A **ParslConfig** instance. 


The optional attribues of a **WorkflowConfig** object are as follows:

* **debug** - Toggles debugging mode for the Workflow (**Default: False**)

* **working_directory** - The parent directory of the Workflow Directory. (**Default: The current working directory**)

* **redo_all_benchmarks** - Toggles whether all tasks are redone upon re-execution of the Workflow or if only incomplete tasks from a previous workflow are completed. (**Default: False**)

* **redo_epic_building** - Toggles whether the ePIC repository is to be re-cloned and re-built. (**Default: False**)

* **redo_simulations** - Toggles whether all **npsim** executions are to be redone. 

* **redo_reconstructions** - Toggles whether all **eicrecon** executions are to be redone. 

* **redo_analysis** - Toggles whether all **analysis** routines are to be redone. 

* **keep_epic_repos** - Toggles whether each **Benchmark's** ePIC repository is kept after a Workflow is completed.

* **keep_simulation_outputs** - Toggles whether the output files of all **npsim** executions are kept after a Workflow is completed. 

* **keep_reconstruction_outputs** - Toggles whether the output files of all **eicrecon** executions are kept after a Workflow is completed. 

* **keep_analysis_outputs** - Toggles whether the output files of all **analysis** routines are kept after a Workflow is completed. 

The following is an example of a **WorkflowConfig** object using a single **BenchmarkConfig** instance
and the **ParslConfig** instance already define previously in their respective sections. 

.. code-block:: python

    from ePIC_benchmarks.workflow import WorkflowConfig

    EXAMPLE_WORKFLOW_CONFIG = WorkflowConfig(
        name="Example Workflow",
        benchmarks=[EXAMPLE_BENCHMARK_CONFIG],
        parsl_config=EXAMPLE_PARSL_CONFIG
    )


A **WorkflowConfig** object can be saved to your filesystem as a configuration file with the following supported file types:

* **YAML** - File Extensions: ".yml", ".yaml"
* **JSON** - File Extension: ".json"

To save a **WorkflowConfig** object (*Using the EXAMPLE_WORKFLOW_CONFIG object as an example*), you can use either of the two following methods:

.. code-block:: python

    EXAMPLE_WORKFLOW_CONFIG.save("path/to/the/desired/file.extension")

or 

.. code-block:: python

    from ePIC_benchmarks.workflow import WorkflowConfig

    WorkflowConfig.save_to_file(EXAMPLE_WORKFLOW_CONFIG, "path/to/the/desired/file.extension")


A configuration file storing the details of a **WorkflowConfig** can also be loaded into a **WorkflowConfig** instance in a python script.
This is done with the following method. 

.. code-block:: python

    from ePIC_benchmarks.workflow import WorkflowConfig

    LOADED_WORKFLOW_CONFIG = WorkflowConfig.load_from_file("path/to/the/saved/file.extension")

Workflow Script
^^^^^^^^^^^^^^^

Why the workflow script is seperate from the workflow configuration
-------------------------------------------------------------------

While the **WorkflowConfig** object stores the configuration parameters of a Workflow, it contains no information on
the desired tasks of a Workflow and their dependencies. 
The tasks to be executed are defined seperately as a python script so that an identical workflow task pattern can be executed for
different workflow configurations. This may be useful to you when you want to...

* complete a Workflow with the same tasks as a previously defined workflow, but with different:

    * Simulation parameters

    * Detector Geometry Updates 

* complete a Workflow with identical Benchmarks on a different computing resource, such as on an HPC with a different cluster manager.

* use an identical workflow configuration for different workflow task patterns. 

App Types
----

A **Workflow Script** is defined with methods that are wrapped by 3 different types of apps:

* **bash_app** An app that executes a program normally executed on the command line. (npsim, eicrecon, echo, etc.)

* **python_app** An app that executes a python function. 

* **join_app** An app that returns the futures of multiple **bash_apps** and/or **python_apps**.

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

**Note:** *The name of the keyword argument to add a dependency does not matter.*
*However, 'kwargs***' *must be added to the app signature.*

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


ePIC Workflow Bash Apps
-----------------------

This package has the following bash apps already defined for your use. 

Container-related Apps
""""""""""""""""""""""

* **pull_containers_app** - Pull a container to be ready for initialization.

ePIC repository-related Apps
""""""""""""""""""""""""""""

* **clone_epic_app** - Clone the ePIC repository into the directory of a Benchmark.

* **checkout_epic_branch_app** - Switch the ePIC repository of a Benchmark to the branch defined in its associated **BenchmarkConfig**.

* **compile_epic_app** - Compile the ePIC repository of a Benchmark.

* **generate_material_map_app** - Generate the material map for the ePIC Repository of a Benchmark.

Simulation-related Apps
"""""""""""""""""""""""

* **run_npsim_app** - Execute npsim with the parameters defined in a specified **SimulationConfig** of a specified **BenchmarkConfig**.

* **run_eicrecon_app** - Execute eicrecon with the parameters defined in a specified **SimulationConfig** of a specified **BenchmarkConfig**.

ePIC Workflow Python Apps
-------------------------

This package has the following python apps already defined for your use. 

Detector Description-related Apps
"""""""""""""""""""""""""""""""""

* **apply_detector_configs_app** - Apply the updates to the ePIC repository's detector geometry files, defined in a **BenchmarkConfig's** list of **DetectorConfigs**.

Analysis-related Apps
"""""""""""""""""""""

* **generate_performance_plots_app** - Generate the tracking performance plots and statistics for a given simulation and benchmark.

Base ePIC Workflow Script
-------------------------

Below is the code for a simple workflow that:

* Retrieves and updates the ePIC Repository for each **Benchmark** with changes stated in its list of **DetectorConfig**.
* Compiles the ePIC Repository for each **Benchmark** and generates the material map if necessary.
* Simulates particle events and reconstructs particle trajectories with **npsim** and **eicrecon** for every **SimulationConfig** of every **BenchmarkConfig**.
* Generates plots and statistics for the tracking performance of every **Simulation** of every **Benchmark**. 

.. code-block:: python

    import numpy as np
    from ePIC_benchmarks.workflow.config import WorkflowConfig
    from ePIC_benchmarks.workflow.bash import bash_app     
    from ePIC_benchmarks.workflow.python import python_app
    from ePIC_benchmarks.workflow.bash.methods.container import pull_containers
    from ePIC_benchmarks.workflow.bash.methods.epic import (
        clone_epic, checkout_epic_branch, compile_epic,
        generate_material_map
    )
    from ePIC_benchmarks.workflow.bash.methods.simulation import run_npsim, run_eicrecon
    from ePIC_benchmarks.workflow.python.methods.detector import apply_detector_configs
    from ePIC_benchmarks.workflow.python.methods.analysis import generate_performance_plots
    from ePIC_benchmarks.container import ShifterConfig
    from parsl import AUTO_LOGNAME
    eicshell_container = ShifterConfig(
        entry_point="/opt/local/bin/eic-shell",
        image="eicweb/jug_xl:25.02.0-stable",
    )
    clone_epic_app = bash_app(clone_epic)
    pull_containers_app = bash_app(pull_containers)
    checkout_app = bash_app(checkout_epic_branch)
    compile_epic_app = bash_app(compile_epic)
    run_npsim_app = bash_app(run_npsim)
    run_eicrecon_app = bash_app(run_eicrecon)
    generate_material_map_app = bash_app(generate_material_map)
    apply_detector_configuration_app = python_app(apply_detector_configs)
    performance_analysis_app = python_app(generate_performance_plots)

    def run(config : WorkflowConfig):
        
        final_futures = []

        pull_containers_future = pull_containers_app(eicshell_container)

        for benchmark_name in config.benchmark_names():
                
                clone_epic_future = clone_epic_app(config, benchmark_name)

                checkout_branch_future = checkout_app(config, benchmark_name,dependency=clone_epic_future)

                update_detectors_future = apply_detector_configuration_app(config, benchmark_name, dependency=checkout_branch_future)

                compile_epic_future = compile_epic_app(config, benchmark_name, num_threads=1, container=eicshell_container, dependency=update_detectors_future, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME)

                generate_material_map_future = generate_material_map_app(config, benchmark_name, nevents=20000, container=eicshell_container, dependency=compile_epic_future)

                for simulation_name in config.simulation_names(benchmark_name):
                                        
                    run_npsim_future = run_npsim_app(config, benchmark_name, simulation_name, container=eicshell_container, dependency=compile_epic_future, stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME)

                    run_eicrecon_future = run_eicrecon_app(config, benchmark_name, simulation_name, use_generated_material_map=True, container=eicshell_container, dependencies=[run_npsim_future, generate_material_map_future], stdout=AUTO_LOGNAME, stderr=AUTO_LOGNAME)

                    analysis_future = performance_analysis_app(
                        config, benchmark_name, simulation_name,
                        dependency=run_eicrecon_future
                    )
                    final_futures.append(analysis_future)
        
        return final_futures 

**Note:** 

* *The above workflow script wraps methods with python and bash apps so that users can customize the Parsl Executor used for each task.*

* *stdout=AUTO_LOGNAME and stderr=AUTO_LOGNAME is used to generate log files for the workflow when debug=True in the Workflow's WorkflowConfig object*

* *'generate_material_map' does nothing when generate_material_map=False for a given BenchmarkConfig*