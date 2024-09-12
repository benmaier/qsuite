#!%s

#SBATCH --cpus-per-task=1
#SBATCH --mem=%s
#SBATCH --array=%d-%d
#SBATCH -o %s
#SBATCH -e %s
#SBATCH --priority=%d

# here go "server_cmds": server specific commands necessary to run the job 
%s

INDEX=$((SLURM_ARRAY_TASK_ID-1))
srun %s %s/job.py $INDEX