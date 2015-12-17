import config_file as cf
import os

jobscript = """
#!/bin/bash
#$ -V
#$ -cwd
#$ -l mem=%s
#$ -t %d-%d

%s %s/job.py $SGE_TASK_ID""" % (cf.jmin,cf.jmax,cf.memory,cf.pythonpath,cf.path)

jobfname = cf.path+"/job.sh"
open(jobfname,'w').write(jobscript).close()
os.system("chmod +x "+jobfname+"; qsub "+jobfname)
