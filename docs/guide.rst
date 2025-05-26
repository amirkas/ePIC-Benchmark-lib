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
**ParslConfig** as well as every **ParslExecutorConfig**, **ParslProviderConfig**, and **ParslLauncherConfig** matches exactly with the objects defined in
the **Parsl** package, a third-party package for Scientific Computing with documentation that can be found '`here <https://parsl.readthedocs.io/en/stable/index.html>`_ '.

When defining your **ParslConfig** object, we highly recommend following the
section in **Parsl's** documentation titled '`Configuring Parsk <https://parsl.readthedocs.io/en/stable/userguide/configuration/index.html>`_ '.
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

While the **WorkflowConfig** object stores the configuration parameters of a Workflow, it contains no information on
the desired tasks of a Workflow and their dependencies. 
The tasks to be executed are defined seperately as a python script so that an identical workflow task pattern can be executed for
different workflow configurations. This may be useful to you when you want to...

* complete a Workflow with the same tasks as a previously defined workflow, but with different:

    * Simulation parameters

    * Detector Geometry Updates 

* complete a Workflow with identical Benchmarks on a different computing resource, such as on an HPC with a different cluster manager.

* use an identical workflow configuration for different workflow task patterns. 

A **Workflow Script** is defined with methods that are wrapped by 3 different types of apps:

* **bash_app** An app that executes a program normally executed on the command line. (npsim, eicrecon, echo, etc.)

* **python_app** An app that executes a python function. 

* **join_app** An app that returns the futures of multiple **bash_app's** and/or **python_app's**.

The following is the required structure of a **Workflow Script**:

.. code-block:: python

    from ePIC_benchmarks.workflow import WorkflowConfig
    from ePIC_benchmarks.workflow.bash import bash_app     
    from ePIC_benchmarks.workflow.python import python_app

    @bash_app
    def example_bash_app(config : WorkflowConfig, other_args):

        #Return the string representation of the command ordinally executed on the Command Line

    @python_app
    def example_python_app(config : WorkflowConfig, other_args):

        #Return the desired output of this python app.

    @bash_app
    def example_another_bash_app(config : WorkflowConfig, other_args):

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

