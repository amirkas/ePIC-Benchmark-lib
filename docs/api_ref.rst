*************
API Reference
*************

Simulation
----------

.. autopydantic_model:: ePIC_benchmarks.simulation.config.SimulationConfig
    :model-show-json: False
    :members:

Detector
--------

.. autopydantic_model:: ePIC_benchmarks.detector.config.DetectorConfig
    :model-show-json: False
    :members:

Benchmark
---------

.. autopydantic_model:: ePIC_benchmarks.benchmark.config.BenchmarkConfig
    :model-show-json: False
    :members:

Parsl
-----

.. autopydantic_model:: ePIC_benchmarks.parsl.config.ParslConfig
    :model-show-json: False
    :members:

Executors
^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.ThreadPoolExecutorConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.HighThroughputExecutorConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.MPIExecutorConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.FluxExecutorConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.executors.executors.WorkQueueExecutorConfig
    :model-show-json: False
    :members:

Providers
^^^^^^^^^

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.AWSProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.CondorProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.GoogleCloudProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.GridEngineProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.LocalProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.LSFProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.SlurmProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.TorqueProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.KubernetesProviderConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.providers.providers.PBSProProviderConfig
    :model-show-json: False
    :members:


Launchers
^^^^^^^^^
.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.SimpleLauncherConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.SingleNodeLauncherConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.SrunLauncherConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.AprunLauncherConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.SrunMPILauncherConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.GnuParallelLauncherConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.MpiExecLauncherConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.MpiRunLauncherConfig
    :model-show-json: False
    :members:

.. autopydantic_model:: ePIC_benchmarks.parsl.launchers.launchers.JsrunLauncherConfig
    :model-show-json: False
    :members:

Workflow
--------

.. autopydantic_model:: ePIC_benchmarks.workflow.config.WorkflowConfig
    :model-show-json: False
    :members:









