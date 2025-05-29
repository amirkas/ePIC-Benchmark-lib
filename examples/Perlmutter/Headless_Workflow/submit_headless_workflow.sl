#!/bin/sh
#SBATCH --nodes=1
#SBATCH --qos=debug
#SBATCH --time=00:30:00
#SBATCH -C cpu

module load python
source activate ePIC_benchmarks

python -m ePIC_benchmarks workflow_config.yml --script=workflow_script.py --funcName=run