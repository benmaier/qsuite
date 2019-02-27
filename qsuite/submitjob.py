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

def get_jobscript(cf,array_id=None):
    JOBSCRIPT = get_dummy(cf.queue)

    if array_id is None:
        arr_id_min = cf.jmin+1
        arr_id_max = cf.jmax+1
    elif type(array_id) in [ list, tuple ] and len(array_id)==2 :
        arr_id_min = array_id[0]
        arr_id_max = array_id[1]
    else:
        arr_id_min = array_id
        arr_id_max = array_id

    jobscript = JOBSCRIPT % (\
                cf.shell,
                cf.memory,
                arr_id_min,
                arr_id_max,
                cf.serverpath+"/output",
                cf.serverpath+"/output",
                cf.priority,
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

def make_job_ready(cf,ssh,array_id=None):

    files_destinations = get_file_list(cf)
    joblocal_names = []

    if type(array_id) is not list and type(array_id) is not tuple:
        is_list = True
        array_id = [ array_id ]
    else:
        is_list = False

    for a_id in array_id:
        jobscript = get_jobscript(cf,a_id)
        print("\nUsing jobscript:\n================")    
        print(jobscript)

        if a_id is not None and (type(a_id) not in [ tuple, list ]):
            joblocalname = os.path.join(os.getcwd(),"."+cf.basename+"_%d.sh" % (a_id))
            jobservername = cf.serverpath+"/"+cf.basename+"_%d.sh" %(a_id)
        elif (type(a_id) in [ tuple, list ]):
            joblocalname = os.path.join(os.getcwd(),"."+cf.basename+"_%d_%d.sh" % tuple(a_id))
            jobservername = cf.serverpath+"/"+cf.basename+"_%d_%d.sh" % tuple(a_id)
        else:
            joblocalname = os.path.join(os.getcwd(),"."+cf.basename+".sh")
            jobservername = cf.serverpath+"/"+cf.basename+".sh"

        f = open(joblocalname,'w')
        f.write(jobscript)
        f.close()

        files_destinations += [ (joblocalname, jobservername) ]
        joblocal_names.append(joblocalname)

    sftp_put_files(ssh,cf,files_destinations)
    
    for joblocalname in joblocal_names:
        qsuite.rm(joblocalname)

    files_chmod_x = [ "chmod +x "+f[1]+"; " for f in files_destinations if f[1].endswith(".sh") ]

    ssh_command(ssh,''.join(files_chmod_x))

    if "execute_after_scp.sh" in cf.files_to_scp:
        ssh_command(ssh,"cd " +cf.serverpath+"; ./execute_after_scp.sh;")


def start_job(cf,ssh,array_id=None):
    """job id procedure taken from https://github.com/osg-bosco/BLAH/blob/1d217fad9c6b54a5e543f7a9d050e77047be0bb1/src/scripts/pbs_submit.sh#L193"""
    if type(array_id) is list or type(array_id) is tuple:
        suffices = ["_%d.sh" % a_id if type(a_id) in [ int ] else "_%d_%d.sh" % tuple(a_id) for a_id in array_id]
    else:
        suffices = [".sh"]
        
    for suffix in suffices:
        if cf.queue=="SGE":
            ssh_command(ssh,"cd " +cf.serverpath+";\
                             jobID=`qsub " + cf.basename + suffix +"`;\
                             jobID=`echo $jobID | awk 'match($0,/[0-9]+/){print substr($0, RSTART, RLENGTH)}'`;\
                             echo $jobID > .jobid;")
        elif cf.queue=="PBS":
            ssh_command(ssh,"cd " +cf.serverpath+";\
                             jobID=`qsub " + cf.basename + suffix +"`;\
                             echo $jobID > .jobid;")
        else:
            print("Unknown queue:",cf.queue)
            sys.exit(1)

    N = len(cf.parameter_list)-1
    filepath = cf.serverpath + "/output/progress_"
    if array_id is None:
        cmd = ('for i in `seq -w 0 %d`; do echo " " > '+filepath+'${i}_%d; done;') % (N,N)
    elif type(array_id) is list or type(array_id) is tuple:
        cmd = ""
        for a_id in array_id:
            if type(a_id) in [ tuple, list ]:
                cmd += (' for i in `seq -w %d %d`; do echo " " > '+filepath+'${i}_%d; done;') % tuple(list(a_id) + [N])
            else:
                cmd += (' echo " " > '+filepath+'%d_%d; done;') % (int(a_id)-1,N)
    else:
        cmd = ('echo " " > '+filepath+'%d_%d; done;') % (int(array_id)-1,N)
    ssh_command(ssh,cmd)
    
