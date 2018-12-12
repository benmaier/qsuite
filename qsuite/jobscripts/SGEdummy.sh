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

INDEX=$((SGE_TASK_ID-1))
%s %s/job.py $INDEX

