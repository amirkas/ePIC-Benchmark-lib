========================
Simulation Configuration 
========================

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

The following is an example code for creating a SimulationConfig instance

.. literalinclude:: example_configs/simulation_config_ex.py
  :language: python