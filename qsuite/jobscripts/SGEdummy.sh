#!%s
#$ -V
#$ -cwd
#$ -l mem=%s
#$ -t %d-%d
#$ -o %s
#$ -e %s
#$ -p %d

# Bash arrays use zero-based indexing but you CAN'T use #$ -t 0-9 (0 is an invalid task id)
if [ -f ~/.bash_profile ]; then
    source ~/.bash_profile
fi

export OMP_NUM_THREADS=1
export USE_SIMPLE_THREADED_LEVEL3=1

# here go "server_cmds": server specific commands necessary to run the job 
%s

INDEX=$((SGE_TASK_ID-1))
%s %s/job.py $INDEX

