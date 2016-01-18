import config_file as cf
import os
import sys

"""
if cf.queue=="SGE":
    jobscript = \"\"\"
#!/bin/bash
#$ -V
#$ -cwd
#$ -l mem=%s
#$ -t %d-%d
#$ -o %s
#$ -e %s

# Bash arrays use zero-based indexing but you CAN'T use #$ -t 0-9 (0 is an invalid task id)
INDEX=$((SGE_TASK_ID-1))
%s %s/job.py $INDEX\"\"\" % (\
                            cf.memory,
                            cf.jmin+1,
                            cf.jmax+1,
                            cf.path+"/output",
                            cf.path+"/output",
                            cf.pythonpath,
                            cf.path)
elif cf.queue=="PBS":
    jobscript = \"\"\"
#!/bin/bash
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
%s %s/job.py $INDEX\"\"\" % (\
                            cf.memory,
                            cf.jmin+1,
                            cf.jmax+1,
                            cf.path+"/output",
                            cf.path+"/output",
                            cf.pythonpath,
                            cf.path)
else:
    print "Queueing architecture " + cf.queue + " unknown"
    sys.exit(1)
"""

jobscript = JOBSCRIPT % (\
            cf.memory,
            cf.jmin+1,
            cf.jmax+1,
            cf.path+"/output",
            cf.path+"/output",
            cf.pythonpath,
            cf.path,
            )

print jobscript
jobfname = cf.path+"/"+cf.name+".sh"

f = open(jobfname,'w')
f.write(jobscript)
f.close()

os.system("chmod +x "+jobfname+"; qsub "+jobfname)
