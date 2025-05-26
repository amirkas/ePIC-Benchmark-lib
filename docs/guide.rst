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

.. code_block:: python

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

.. code_block:: python

    from ePIC_benchmarks.detector import DetectorConfig
    from ePIC_benchmarks.detector.xml_elements.detector import (
        XmlDetectorElement, XmlModuleElement,
        XmlModuleComponentElement, XmlFrameElement,
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

.. code_block:: python

    from ePIC_benchmarks.benchmark import BenchmarkConfig

    EXAMPLE_BENCHMARK_CONFIG = BenchmarkConfig(
        simulation_configs=[EXAMPLE_SIMULATION_CONFIG],
        detector_configs=[EXAMPLE_DETECTOR_CONFIG],
        epic_branch="main",
        generate_material_map=False
    )

ParslConfig
-----------

.. code_block:: python

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


ParslExecutorConfig
-------------------

ParslProviderConfig
-------------------

ParslLauncherConfig
-------------------

WorkflowConfig
--------------

.. code_block:: python

    from ePIC_benchmarks.workflow import WorkflowConfig

    EXAMPLE_WORKFLOW_CONFIG = WorkflowConfig(
        name="Example Workflow",
        benchmarks=[EXAMPLE_BENCHMARK_CONFIG],
        parsl_config=EXAMPLE_PARSL_CONFIG
    )



