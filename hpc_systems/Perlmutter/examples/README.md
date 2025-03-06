# Perlmutter ePIC workflow examples

## Headless Workflow

***Execute workflows locally on a compute node, bypassing the need to keep a login node running for workflow completion***

1. Copy 'headless_workflow_config.py', 'headless_workflow.sl', and 'workflow_scipt.py' to your preferred working directory.

2. Define your workflow using 'headless_workflow_config.py' as a template. 

3. Define your desired QOS, walltime, and number of nodes in 'headless_workflow.sl'

4. To execute the workflow, run this command in your working directory

```
sbatch headless_workflow.sl
```

5. To track progress of tasks, inspect 'runinfo/task_logs' within your workflow directory for stdout / stderrs

## Local Slurm job submission workflow

***Executes workflows by submitting jobs to Slurm from your login node.***

***This requires that both your login node, and the parent process of the workflow stay alive during the duration of execution***

1. Copy 'local_slurm_workflow_config.py' and 'workflow_script.py' to your preferred working directory

2. Define your workflow using 'local_slurm_workflow_config.py' as a template. 

3. To execute your workflow, run the following commands in your terminal:

```
cd {your_working_directory}
module load python
conda activate ePIC_benchmarks
python local_slurm_workflow_config.py
```
