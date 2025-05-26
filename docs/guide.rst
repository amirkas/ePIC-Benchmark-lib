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

The DetectorConfig object is used to dynamically alter the ePIC detector geometry before its compilation.

Each detector geometry file in the ePIC repository has a tree-like structure of XML elements with different tags and attributes.
Making changes to an XML element requires that a query be constructed to find the XML element of interest.
This library manages query construction for you, but you must define the XML tree associated with the query.
This is done with the use of XML element objects defined in the submodules of **ePIC_benchmarks.detector.xml_elements**.

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

To construct a query such that the **'sensitive'** attribute of **every XmlModuleComponentElement**
of **every XmlModuleElement** of **every XmlDetectorElement** is updated to be **false**,
we would define the following XML tree:

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
we would define the following XML tree:

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

To integrate this change into a workflow, for the **tracking/silicon_disks.xml** detector description file,
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

WorkflowConfig
--------------

The **WorkflowConfig** object is the root 

.. code-block:: python

    from ePIC_benchmarks.workflow import WorkflowConfig

    EXAMPLE_WORKFLOW_CONFIG = WorkflowConfig(
        name="Example Workflow",
        benchmarks=[EXAMPLE_BENCHMARK_CONFIG],
        parsl_config=EXAMPLE_PARSL_CONFIG
    )



