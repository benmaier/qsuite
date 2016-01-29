#!%s
#taken from http://www.uibk.ac.at/zid/systeme/hpc-systeme/common/tutorials/pbs-howto.html#HDR1_1
#PBS -l ncpus=1
#PBS -l mem=%s
#PBS -t %d-%d
#PBS -o %s
#PBS -e %s
#PBS -p %d

# Change to current working directory (directory where qsub was executed)
# within PBS job (workaround for SGE option "-cwd")
cd $PBS_O_WORKDIR

INDEX=$((PBS_ARRAYID-1))
%s %s/job.py $INDEX
