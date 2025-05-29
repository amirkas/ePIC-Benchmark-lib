*************
API Reference
*************

Simulation
==========

Config
------

SimulationConfig
^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.simulation.config.SimulationConfig
    :model-show-json: False
    :members:

Detector
========

Config
------

DetectorConfig
^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.detector.config.DetectorConfig
    :model-show-json: False
    :members:

XML Elements
------------

Detector XML Elements
^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlDetectorElement
    :model-show-json: False
    :model-erdantic-figure: True
    :model-erdantic-figure-collapsed: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlModuleElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlModuleComponentElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlTrdElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlFrameElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlLayerElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlLayerMaterialElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlRphiLayoutElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlBarrelEnvelopeElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlZLayoutElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlEnvelopeElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlRingElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlDimensionsElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.detector.detector.XmlTypeFlagsElement
    :model-show-json: False
    :members:

Constant XML Elements
^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.constant.constant.XmlConstantElement
    :model-show-json: False
    :members:
    :model-erdantic-figure: True
    :model-erdantic-figure-collapsed: False

Plugin XML Elements
^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.plugins.plugins.XmlArgumentElement
    :model-show-json: False
    :members:
    :model-erdantic-figure: True
    :model-erdantic-figure-collapsed: False

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.plugins.plugins.XmlPluginElement
    :model-show-json: False
    :members:
    :model-erdantic-figure: True
    :model-erdantic-figure-collapsed: False

Readout XML elements
^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.readout.readout.XmlReadoutElement
    :model-show-json: False
    :members:
    :model-erdantic-figure: True
    :model-erdantic-figure-collapsed: False

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.readout.readout.XmlSegmentationElement
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.detector.xml_elements.readout.readout.XmlReadoutIdElement
    :model-show-json: False
    :members:
    :model-erdantic-figure: True
    :model-erdantic-figure-collapsed: False

Benchmark
=========

Config
------

BenchmarkConfig
^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.benchmark.config.BenchmarkConfig
    :model-show-json: False
    :members:

Parsl
=====

Config
------

ParslConfig
^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.config.ParslConfig
    :model-show-json: False
    :members:

Executors
---------

ThreadPoolExecutorConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.ThreadPoolExecutorConfig
    :model-show-json: False
    :members:

HighThroughputExecutorConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.HighThroughputExecutorConfig
    :model-show-json: False
    :members:

MPIExecutorConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.MPIExecutorConfig
    :model-show-json: False
    :members:

FluxExecutorConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.FluxExecutorConfig
    :model-show-json: False
    :members:

WorkQueueExecutorConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.WorkQueueExecutorConfig
    :model-show-json: False
    :members:



Providers
---------

AWSProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.AWSProviderConfig
    :model-show-json: False
    :members:

CondorProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.CondorProviderConfig
    :model-show-json: False
    :members:

GoogleCloudProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.GoogleCloudProviderConfig
    :model-show-json: False
    :members:

GridEngineProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.GridEngineProviderConfig
    :model-show-json: False
    :members:

LocalProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.LocalProviderConfig
    :model-show-json: False
    :members:

LSFProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.LSFProviderConfig
    :model-show-json: False
    :members:

SlurmProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.SlurmProviderConfig
    :model-show-json: False
    :members:

TorqueProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.TorqueProviderConfig
    :model-show-json: False
    :members:

KubernetesProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.KubernetesProviderConfig
    :model-show-json: False
    :members:

PBSProProviderConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.PBSProProviderConfig
    :model-show-json: False
    :members:


Launchers
---------

SimpleLauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.SimpleLauncherConfig
    :model-show-json: False
    :members:

SingleNodeLauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.SingleNodeLauncherConfig
    :model-show-json: False
    :members:

SrunLauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.SrunLauncherConfig
    :model-show-json: False
    :members:

AprunLauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.AprunLauncherConfig
    :model-show-json: False
    :members:

SrunMPILauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.SrunMPILauncherConfig
    :model-show-json: False
    :members:

GnuParallelLauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.GnuParallelLauncherConfig
    :model-show-json: False
    :members:

MpiExecLauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.MpiExecLauncherConfig
    :model-show-json: False
    :members:

MpiRunLauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.MpiRunLauncherConfig
    :model-show-json: False
    :members:

JsrunLauncherConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.JsrunLauncherConfig
    :model-show-json: False
    :members:

Workflow
========

Config
------

WorkflowConfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.workflow.config.WorkflowConfig
    :model-show-json: False
    :members:

.. _paths-api:

Paths API
---------

.. autoclass:: ePIC_benchmarks.workflow._inner.paths.WorkflowPaths
    :members:
    :undoc-members:

Executor API
------------

.. autoclass:: ePIC_benchmarks.workflow._inner.executor.WorkflowExecutor
    :members:
    :undoc-members:









