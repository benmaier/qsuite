import os
import sys
import qsuite
import paramiko

def get_dummy(qname):
    originaldummy = os.path.join(qsuite.__path__[0],"jobscripts",qname+"dummy.sh")
    s = open(originaldummy,'r').read()

    return s

def get_jobscript(s,cf):
    pass

def submit_job(cf,qsuiteparser):

    JOBSCRIPT = get_dummy(cf.queue)

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
    joblocalname = os.path.join(os.getcwd(),cf.name+".sh")
    jobserver = os.path.join(os.getcwd(),"__"+cf.name+".sh")

    f = open(joblocalname,'w')
    f.write(jobscript)
    f.close()

    os.system("chmod +x "+jobfname+"; qsub "+jobfname)
    
