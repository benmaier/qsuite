#!/bin/%s
#taken from http://www.uibk.ac.at/zid/systeme/hpc-systeme/common/tutorials/pbs-howto.html#HDR1_1
#PBS -l ncpus=1
#PBS -l mem=%s
#PBS -J %d-%d
# Redirect output stream to this dir
#PBS -o %s

# Redirect error stream to this dir
#PBS -e %s

# Change to current working directory (directory where qsub was executed)
# within PBS job (workaround for SGE option "-cwd")
cd $PBS_O_WORKDIR

INDEX=$((PBS_ARRAY_INDEX-1))
%s %s/job.py $INDEX
