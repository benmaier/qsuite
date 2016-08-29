from __future__ import print_function
import os
import sys
import qsuite
from qsuite import qconfig
import ast
from qsuite import get_template_file
from qsuite import copy_template
from qsuite import set_default_file 
from qsuite import get_qsuite
from qsuite import set_in_qsuite
from qsuite import rm_in_qsuite
from qsuite import write_qsuite
from qsuite import rm 
from qsuite import reset 
from qsuite import ssh_command 
from qsuite import ssh_connect
from qsuite import make_job_ready
from qsuite import start_job
from qsuite import sftp_put_files
from qsuite import sftp_get_files
from qsuite import mkdirp
from qsuite import print_params
from qsuite import print_status
from qsuite import print_params_and_status
from qsuite.queuesys.job import job
import shutil
import re

if sys.version_info[0] == 3:
    raw_input = input

def update_git(cf,ssh):
    repos = cf.git_repos

    #ssh.connect(cf.server,username=cf.username)
    repostring = ''
    for repo in cf.git_repos:

        if len(repo)==3:
            repostring += 'if [ ! -d "%s" ]; then\ngit clone %s %s\nfi\n' % (repo[0],repo[2],repo[0])

        repostring += "cd %s; git fetch; git pull; %s; " % tuple(repo[:2])

    if len(cf.git_repos)>0 :
        ssh_command(ssh,repostring)


def wrap_results(cf,ssh):
    ssh_command(ssh, "cd " + cf.serverpath + "; " + cf.pythonpath + " wrap_results.py;")
    ssh_command(ssh, "cd " + cf.serverpath + "/results; gzip results.p" )
    ssh_command(ssh, "cd " + cf.serverpath + "/results; gzip times.p" )
    custom_wrap_results(cf,ssh)

def custom_wrap_results(cf,ssh):
    if "custom_wrap_results.py" in cf.files_to_scp:
        ssh_command(ssh, "cd " + cf.serverpath + "; " + cf.pythonpath + " custom_wrap_results.py;")

def wrap_local(cf):

    files = list(cf.files_to_scp.values()) + cf.additional_files_to_scp
    mkdirp(cf.localpath)
    for f in files:
        shutil.copy2(f,cf.localpath)

def qstat(cf,ssh,args):
    if len(args)==0:
        flag = "-u " + cf.username
        ssh_command(ssh,"qstat "+flag)

    elif args[0] == "job":
        if cf.queue=="SGE":
            flag = "-j"
        elif cf.queue=="PBS":
            flag = ""
        else:
            print("Queue",cf.queue,"not supported.")
            sys.exit(1)
        ssh_command(ssh,"qstat "+flag+" $(cat "+cf.serverpath+"/.jobid)")

    elif args[0] == "all":
        if cf.queue=="SGE":
            flag = '-u "*"'
        elif cf.queue=="PBS":
            flag = "-Q"
        else:
            print("Queue",cf.queue,"not supported.")
            sys.exit(1)
        ssh_command(ssh,"qstat "+flag)


def init(qsuitefile,opts):
    qsuiteparser = get_qsuite(qsuitefile,init=True)
    copy_template("config",opts)
    copy_template("simulation",opts)
    write_qsuite(qsuiteparser,qsuitefile)



def main():
    
    #create the custom dir if it doesn't exist yet

    if len(sys.argv)==1:
        print("Yes, I'm here! Give me a command!")
        sys.exit(1)

    args = [ a for a in sys.argv[1:] if not a.startswith("-") ]
    opts = [ a for a in sys.argv[1:] if a.startswith("-") ]

    cmd = args[0]
    cwd = os.getcwd()
    qsuitefile = os.path.join(cwd,".qsuite")

    cf = None
    qsuiteparser = None

    git_cmds = ["git","gitupdate","git_update","updategit","update_git"]
    prep_cmds = [ "prepare", "make", "makeready" ]
    submit_cmds = [ "submit", "start", "submit_job"]
    set_cmds = ["set"]
    reset_cmds = ["reset", "resetdefault"]
    add_cmds = ["add"]
    rm_cmds = ["rm","remove"]
    wrap_cmds = ["wrap","wrapresults","wrap_results"]
    qstatus_cmds = ["qstat","qstatus"]
    status_cmds = ["stat","status"]
    ssh_cmds = ["ssh"]
    sftp_cmds = ["sftp","scp","ftp","put"]
    customwrap_cmds = ["customwrap"]
    get_cmds = ["get"]
    test_cmds = ["test"]
    err_cmds = ["err","error"]
    param_cmds = ["params"]

    if cmd in ["init","initialize"]:
        if len(args)==1:
            if not os.path.exists(qsuitefile):
                init(qsuitefile,opts)
                sys.exit(0)
            else:
                yn = raw_input("There's already a .qsuite file carrying configurations. Do you want to override it (y/n)? ")
                yn = yn.lower()[0]
                if yn == "y":
                    init(qsuitefile,opts)
                sys.exit(0)
        elif len(args)>1:
            if args[1] in ["customwrap", "customwrapper"]:
                copy_template("customwrap",opts)
                sys.exit(0)
            else:
                print("Unknown option",args[1])
                sys.exit(1)
    elif not os.path.exists(os.path.join(cwd,".qsuite")):
        if (    (cmd not in set_cmds) \
             or (len(args)<2) \
             or (not args[1].startswith("default")) ):
          
            #if there's no ".qsuite" file yet, stop operating
            print("Not initialized yet!")
            sys.exit(1)
    elif cmd in (git_cmds + submit_cmds + prep_cmds + reset_cmds + add_cmds + rm_cmds +\
                 set_cmds + wrap_cmds + status_cmds + ssh_cmds + sftp_cmds + customwrap_cmds +\
                 get_cmds + test_cmds + param_cmds + qstatus_cmds + err_cmds):

        #I do this to prevent that the default stuff can only be set in an initialized dir
        if not (cmd in set_cmds and len(args)>1 and args[1].startswith("default")):
            qsuiteparser = get_qsuite(qsuitefile)

        if cmd in set_cmds:
            if len(args)>2:

                thing_to_set = args[1]
                set_to_thing = args[2]

                if thing_to_set in ["cfg", "config", "configuration"]:
                    set_in_qsuite(qsuiteparser,qsuitefile,"config",set_to_thing)
                elif thing_to_set in ["sim", "simulation"]:
                    set_in_qsuite(qsuiteparser,qsuitefile,"simulation",set_to_thing)
                elif thing_to_set in ["customwrap", "customwrapper"]:
                    set_in_qsuite(qsuiteparser,qsuitefile,"customwrap",set_to_thing)
                elif thing_to_set in ["exec", "execute", "exe"]:
                    set_in_qsuite(qsuiteparser,qsuitefile,"exec",set_to_thing)

                elif thing_to_set.startswith("default"):
                    if len(args)>2:

                        file_to_set = args[2]

                        if thing_to_set in ["defaultcfg", "defaultconfig", "defaultconfiguration"]:
                            set_default_file("config",file_to_set)
                        elif thing_to_set in ["defaultsim", "defaultsimulation"]:
                            set_default_file("simulation",file_to_set)
                        elif thing_to_set in ["defaultwrap", "defaultcustomwrap", "defaultcustomwrapper"]:
                            set_default_file("customwrap",file_to_set)
                        sys.exit(0)
                    else:
                        print("No default file given.")
                        sys.exit(1)
                else:
                    print("Option "+ thing_to_set +" not known.")
                    sys.exit(1)
                sys.exit(0)
            elif len(args)==2:
                thing_to_set = args[1]
                if thing_to_set in ["custom_wrap_results.py"]:
                    set_in_qsuite(qsuiteparser,qsuitefile,"customwrap",thing_to_set)
            else:
                print("Nothing to set!")
                sys.exit(1)

        elif cmd in reset_cmds:
            if len(args)>1:

                things_to_reset = args[1:]
                for thing_to_reset in things_to_reset:
                    if thing_to_reset in ["defaultcfg", "defaultconfig", "defaultconfiguration"]:
                        reset("config")
                    elif thing_to_reset in ["defaultsim", "defaultsimulation"]:
                        reset("simulation")
                    elif thing_to_reset in ["defaultwrap", "defaultcustomwrap", "defaultcustomwrapper"]:
                        reset("customwrap")
                sys.exit(0)
            else:
                print("Nothing to reset given.")
                sys.exit(1)

        elif cmd in add_cmds:

            if len(args)>1:
                thing_to_set = args[1:]

                if "custom_wrap_results.py" in thing_to_set:
                    set_in_qsuite(qsuiteparser,qsuitefile,"customwrap","custom_wrap_results.py")
                    thing_to_set.pop(thing_to_set.index("custom_wrap_results.py"))

                if len(thing_to_set)>0:
                    set_in_qsuite(qsuiteparser,qsuitefile,"add",thing_to_set)

                sys.exit(0)
            else:
                print("Nothing to add!")
                sys.exit(1)

        elif cmd in rm_cmds:
            if len(args)>1:
                thing_to_set = args[1:]
                rm_in_qsuite(qsuiteparser,qsuitefile,thing_to_set)
                sys.exit(0)
            else:
                print("Nothing to remove!")
                sys.exit(1)

        elif cmd in test_cmds:
            if len(args)==1:
                jobid = 0
                respath = os.path.join(os.getcwd(),".test")
            elif len(args)==2:
                jobid = int(args[1])
                respath = os.path.join(os.getcwd(),".test")
            elif len(args)>2:
                jobid = int(args[1])
                respath = args[2]

            cf = qconfig(qsuiteparser=qsuiteparser)
            sys.path.insert(1,os.getcwd()) #add current working directory to import paths
            job(jobid,respath,cf)
            sys.exit(0)                

        elif cmd in param_cmds:
            cf = qconfig(qsuiteparser=qsuiteparser)
            print_params(cf)

        elif cmd in git_cmds + prep_cmds + submit_cmds + wrap_cmds + status_cmds +\
                    ssh_cmds + sftp_cmds + customwrap_cmds + get_cmds + qstatus_cmds + err_cmds:

            cf = qconfig(qsuiteparser=qsuiteparser)
            ssh = ssh_connect(cf)

         
            if cmd in git_cmds:
                update_git(cf,ssh)
                sys.exit(0)        
            elif cmd in prep_cmds:
                update_git(cf,ssh)
                make_job_ready(cf,ssh)
                wrap_local(cf)
                sys.exit(0)
            elif cmd in submit_cmds:
                cmds = args[1:]
                if len(cmds)>0:
                    array_id = [ int(c) if ("-" not in c) else [ int(rangeid) for rangeid in c.split("-") ] for c in cmds]
                    print("Using array IDs "+str(array_id)+". Beware! Array IDs start counting at 1.")
                else:
                    array_id = None
                    update_git(cf,ssh)

                make_job_ready(cf,ssh,array_id)
                
                if array_id is None:
                    wrap_local(cf)

                start_job(cf,ssh,array_id)

                sys.exit(0)
            elif cmd in wrap_cmds:
                wrap_results(cf,ssh)
                ssh_command
                sys.exit(0)
            elif cmd in customwrap_cmds:
                custom_wrap_results(cf,ssh)
                sys.exit(0)
            elif cmd in qstatus_cmds:
                cmds = args[1:]
                qstat(cf,ssh,cmds)
                sys.exit(0)
            elif cmd in status_cmds:
                cmds = args[1:]
                if len(cmds)>0:
                    print_params_and_status(cf,ssh)
                else:
                    print_status(cf,ssh)
                sys.exit(0)
            elif cmd in err_cmds:
                cmds = args[1:]
                if len(cmds)>0:
                    array_id = str(int(cmds[0]))
                else:
                    array_id = "1"
                print("Using array ID "+array_id+". Beware! Array IDs start counting at 1.")
                ssh_command(ssh,"cat "+cf.serverpath+"/output/"+cf.basename+".sh.e$(cat "+cf.serverpath+"/.jobid)."+array_id)
                sys.exit(0)
            elif cmd in ssh_cmds:
                cmds = args[1:]
                ssh_command(ssh," ".join(cmds))
                sys.exit(0)
            elif cmd in sftp_cmds:
                files = args[1:]
                files_dests = [ (f,cf.serverpath+"/"+f) for f in files ]
                sftp_put_files(ssh,cf,files_dests)
            elif cmd in get_cmds:
                #get the wrapped result
                if len(args)>1 and args[1] not in ["all","results","allresults"]:
                    filenames = args[1:]
                    local_filenames = [ f.split('/')[-1] for f in filenames ]
                    files_dests = [ (cf.serverpath+"/"+f, os.path.join(cwd,cf.localpath,local_f)) \
                                    for f,local_f in zip(filenames,local_filenames) ]
                    sftp_get_files(ssh,cf,files_dests)
                else:
                    get_all =  len(args)>1 and args[1] in ["all","allresults"]

                    pattern_res = re.compile(r'result.*\.p*$')
                    pattern_tim = re.compile(r'time.*\.p*$')
                    resultstring = ssh_command(ssh,"ls "+cf.resultpath)
                    resultstring = resultstring.replace("\n"," ")
                    resultlist = [ f for f in resultstring.split(" ") if (f!="" and not f.startswith(".")) ]
                    resultlist = [ r for r in resultlist if not ((not get_all) and ((pattern_res.match(r)) or (pattern_tim.match(r)))) ]

                    files_dests = [ (cf.resultpath+"/"+f, os.path.join(cwd,cf.localpath,f)) for f in resultlist ]
                    sftp_get_files(ssh,cf,files_dests)

            else:
                pass
    else:
        print("Command",cmd,"unknown.")


