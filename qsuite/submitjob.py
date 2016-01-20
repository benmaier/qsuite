import os
import sys
import qsuite
from qsuite import sftp_put_files
from qsuite import ssh_command

def get_dummy(qname):
    potential_file = os.path.join(qsuite.customdir,qname+"dummy.sh")
    if not os.path.exists(potential_file):
        potential_file = os.path.join(qsuite.__path__[0],"jobscripts",qname+"dummy.sh")
    s = open(potential_file,'r').read()

    return s

def get_jobscript(cf):
    JOBSCRIPT = get_dummy(cf.queue)

    jobscript = JOBSCRIPT % (\
                cf.memory,
                cf.jmin+1,
                cf.jmax+1,
                cf.serverpath+"/output",
                cf.serverpath+"/output",
                cf.pythonpath,
                cf.serverpath,
                )
    return jobscript

def get_file_list(cf):
    
    files_destinations = [            
            ( 
                os.path.join(qsuite.__path__[0],"queuesys","wrap_results.py"),
                cf.serverpath + "/wrap_results.py" 
            ),
            (
                os.path.join(qsuite.__path__[0],"queuesys","job.py"),
                cf.serverpath + "/job.py"
            ),
            (
                os.path.join(qsuite.__path__[0],"qconfig.py"),
                cf.serverpath + "/qconfig.py"
            ),
        ]

    local_files = [  ( os.path.join(os.getcwd(),lname),  cf.serverpath + "/" + sname ) for sname,lname in cf.files_to_scp.items() ]

    add_files = [ ( os.path.join(os.getcwd(),aname),  cf.serverpath + "/" + aname ) for aname in cf.additional_files_to_scp  ]

    files_destinations += local_files + add_files

    return files_destinations

def make_job_ready(cf,ssh):

    jobscript = get_jobscript(cf)
    print("\nUsing jobscript:\n================")    
    print(jobscript)

    joblocalname = os.path.join(os.getcwd(),"."+cf.basename+".sh")
    jobservername = cf.serverpath+"/"+cf.basename+".sh"

    f = open(joblocalname,'w')
    f.write(jobscript)
    f.close()

    files_destinations = get_file_list(cf)
    files_destinations += [ (joblocalname, jobservername) ]

    sftp_put_files(ssh,cf,files_destinations)

    qsuite.rm(joblocalname)

    files_chmod_x = [ "chmod +x "+f[1]+"; " for f in files_destinations if f[1].endswith(".sh") ]

    ssh_command(ssh,''.join(files_chmod_x))
    ssh_command(ssh,"cd " +cf.serverpath+"; ./execute_after_scp.sh;")

def start_job(cf,ssh):
    ssh_command(ssh,"cd " +cf.serverpath+"; qsub " + cf.basename + ".sh;")
    
