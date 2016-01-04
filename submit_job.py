import config_file as cf
import os

jobscript = """
#!/bin/bash
#$ -V
#$ -cwd
#$ -l mem=%s
#$ -t %d-%d
#$ -o %s
#$ -e %s

# Bash arrays use zero-based indexing but you CAN'T use #$ -t 0-9 (0 is an invalid task id)
INDEX=$((SGE_TASK_ID-1))
%s %s/job.py $INDEX""" % (\
                            cf.memory,
                            cf.jmin+1,
                            cf.jmax+1,
                            cf.path+"/output",
                            cf.path+"/output",
                            cf.pythonpath,
                            cf.path)

jobfname = cf.path+"/"+cf.name+".sh"
f = open(jobfname,'w')
f.write(jobscript)
f.close()
os.system("chmod +x "+jobfname+"; qsub "+jobfname)
