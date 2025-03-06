#!/bin/sh
#SBATCH --nodes=1
#SBATCH --qos=regular
#SBATCH --time=02:00:00
#SBATCH -C cpu

module load python
source activate ePIC_benchmarks

python workflow.py