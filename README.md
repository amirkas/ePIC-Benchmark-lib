# Electron-Proton Ion Collider Benchmark Library

## Description:
- The library has been developed to standardize and automate the execution of detector benchmarks over all iterations of the ePIC design.
- Under the hood, simulations are run using npsim and eicrecon, which are contained within the eicshell container available as a stable or nightly build.
- The library contains multiple modules to support benchmark workflows, such as configuration & filesystem management, execution configuration on various systems (local, HPC, etc.), and data analytic tools

## Installation

# Requirements:
- **Conda** 
	*(Installation instructions for your system can be found at https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)*

# Download library from git with HTTP:

**Using HTTP:**
   ```
   git clone https://github.com/amirkas/ePIC-Benchmark-lib.git
   ```
# Access the library directory:
  ```
  cd ePIC-Benchmark-Lib
  ```
# Create the conda environment from the library's environment.yml configuration
  ```
  conda env create -f environment.yml
  ```

## Using the library:

# Activating the conda environment

  ```
	conda activate epic_benchmarks
  ```
  

## For developers

# To update the conda environment after editing the source code.

```
cd /path/to/ePIC_Benchmark-Lib
```

```
conda env update --file environment.yml --prune
```
	
	

### Modules to support benchmark workflows:

**Under Construction**

