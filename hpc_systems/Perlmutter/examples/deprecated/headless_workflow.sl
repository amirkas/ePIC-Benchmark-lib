#!/bin/sh
#SBATCH --nodes=1
#SBATCH --qos=regular
#SBATCH --time=04:00:00
#SBATCH -C cpu

module load python
source activate ePIC_benchmarks

python headless_workflow_config.py 