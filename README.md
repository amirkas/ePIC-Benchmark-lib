# Electron-Proton Ion Collider Benchmark Library

## Description:
- The library has been developed to standardize and automate the execution of detector benchmarks over all iterations of the ePIC design.
- Under the hood, simulations are run using npsim and eicrecon, which are contained within the eicshell container available as a stable or nightly build.
- The library contains multiple modules to support benchmark workflows, such as configuration & filesystem management, execution configuration on various systems (local, HPC, etc.), and data analytic tools

# Installation

## Requirements:
- **Conda** 
	*(Installation instructions for your system can be found at https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)*

### Download library from git with HTTP:

**Using HTTP:**
```
git clone https://github.com/amirkas/ePIC-Benchmark-lib.git
```
### Access the library directory:
```
cd ePIC-Benchmark-lib
```
### Create the conda environment from the library's environment.yml configuration
```
conda env create -f environment.yml
```

# Using the library:

### Activating the conda environment

```
conda activate ePIC_benchmarks
```

### The Workflow Hierarchy:


A workflow is defined as a nested class structure that is YAML, JSON, and XAML compatible.
Below is the general structure of a workflow configuration with nested configuration classes marked in **Bold**, and a description of each class marked in *Italic* :

- **WorkflowConfig**:
	- *Contains list of all benchmarks to run in 1 submission to a cluster manager / local system thread scheduler + additional options such as setting which files/folders to keep, turning on debugging output, etc.*
	- List of **BenchmarkConfigs**
		- *Defines the configuration for an ePIC repository for a set of simulations. Also defines the naming convention for the workflow file system. Configuration for a Benchmark's ePIC repository include:*
			- Current Branch
			- List of changes to Detector Description Files via **DetectorConfig**
		- List of **SimulationConfigs**
			- *Defines the configuration for **npsim** and **eicrecon** execution*
		- List of **DetectorConfigs**
			- *Defines the configuration for 1 update to an ePIC detector description xml file. An update type is one of be 'SET', 'ADD', or 'DELETE'*
	- **ParslConfig**
		- *Defines the configuration for parsl job submissions*
		- List of **ParslExecutorConfigs**
			- *Defines the configuration for one of parsl's job submission executor strategies which include:*
				- **High Throughput Executor Config** which submits jobs  
				




### Workflow classes

#### Workflow Config





### Defining a workflow
	
```
A Workflow configuration contains 1 or more benchmarks to run, and a parsl config to execute all the benchmarks.
A Benchmark configuration contains at 1 or more simulation configurations that can be run with npsim and/or eicrecon
A Benchmark configuration contains 0 or more detector configs that can dynamically update ePIC detector xml files
A Parsl configuration defines how parsl should distribute tasks. This depends on your workflow needs, and your system's available providers and hardware constraints.

Examples listed in the examples folder show how a workflow can be defined, saved as a yaml/json file, and executed.
```
	


## For developers

### To update the conda environment after editing the source code.

```
cd /path/to/ePIC-Benchmark-lib
```

```
conda env update --file environment.yml --prune
```

### Updating your IDE's intellisense

```
Set the mypy config file location in your IDE settings to /path/to/ePIC-Benchmark-lib/ePIC_benchmarks/mypy.ini
```
	
	

### Modules to support benchmark workflows:

**Under Construction**

