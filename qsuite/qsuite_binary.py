from __future__ import print_function
import os
import sys
import qsuite
import subprocess
import math 

from functools import reduce
import operator

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
from qsuite.printparams import _get_progress_sftp
import shutil
import re

from operator import itemgetter
from itertools import groupby

from pathos.multiprocessing import ProcessingPool as Pool
from functools import partial

try:
    # Python 2
    import cPickle as pickle
except ImportError:
    # Python 3
    import pickle
    basestring = str

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
    test_cmds = ["test", "local"]
    err_cmds = ["err","error"]
    param_cmds = ["params"]
    convert_cmds = ["convert"]
    estimation_cmds = ["estimate", "estimatespace", "data"]

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
    elif not os.path.exists(os.path.join(cwd,".qsuite")) and not cmd in convert_cmds:
        if (    (cmd not in set_cmds) \
             or (len(args)<2) \
             or (not args[1].startswith("default")) ):

            #if there's no ".qsuite" file yet, stop operating
            print("Not initialized yet!")
            sys.exit(1)
    elif cmd in convert_cmds:
        #convert to numpy and calculate mean and error
        #only works in results directory!
        cf = qconfig()

        cmds = args[1:]
        if len(cmds)==0:
            cmds = ["numpy"]

        # numpy is imported here because I don't want to make qsuite
        # dependent on it, and this will give an error on runtime,
        # not when qsuite is started
        import numpy as np

        data_already_loaded = False

        if "numpy" in cmds or \
           (any([c in cmds for c in ["meanerr","nanmeanerr","meanstd","nanmeanstd","defaultpercentiles","percentiles","quartiles"]]) and not os.path.exists("results.npy")):

            if not os.path.exists(os.path.join(cwd, "results.p")):
                p = subprocess.Popen(["gzip", "-d", "results.p.gz"])
                exit_code = p.wait() 
                if exit_code == 1:
                    print("error while using gzip -d results.p.gz")
                    sys.exit(1)

            try:
                data = pickle.load(open("results.p","rb"))
            except UnicodeDecodeError:
                data = pickle.load(open("results.p","rb"), encoding='latin1')

            data = np.array(data)
            np.save("results.npy",data)
            data_already_loaded = True

        if "meanerr" in cmds:
            if not data_already_loaded:
                data = np.load("results.npy")

            axis = None
            if isinstance(axis,basestring) or axis is None:
                axis = (cf.parameter_names+cf.internal_names).index(axis)

            N = len((cf.external_parameters+cf.internal_parameters)[axis][1])
            mn, err = data.mean(axis=axis), data.std(axis=axis)/np.sqrt(N)
            np.savez("./results_mean_err.npz",mean=mn,err=err)

        if "nanmeanerr" in cmds:
            if not data_already_loaded:
                data = np.load("results.npy")

            axis = None
            if isinstance(axis,basestring) or axis is None:
                axis = (cf.parameter_names+cf.internal_names).index(axis)

            N = len((cf.external_parameters+cf.internal_parameters)[axis][1])
            mn, err = np.nanmean(data,axis=axis), np.nanstd(data,axis=axis)/np.sqrt(N)
            np.savez("./results_mean_err.npz",mean=mn,err=err)

        if "meanstd" in cmds:
            if not data_already_loaded:
                data = np.load("results.npy")

            axis = None
            if isinstance(axis,basestring) or axis is None:
                axis = (cf.parameter_names+cf.internal_names).index(axis)

            mn, err = data.mean(axis=axis), data.std(axis=axis)
            np.savez("./results_mean_std.npz",mean=mn,std=err)

        if "nanmeanstd" in cmds:
            if not data_already_loaded:
                data = np.load("results.npy")

            axis = None
            if isinstance(axis,basestring) or axis is None:
                axis = (cf.parameter_names+cf.internal_names).index(axis)

            N = len((cf.external_parameters+cf.internal_parameters)[axis][1])
            mn, err = np.nanmean(data,axis=axis), np.nanstd(data,axis=axis)
            np.savez("./results_mean_std.npz",mean=mn,std=err)

        percentiles_name = None

        if "defaultpercentiles" in cmds:
            percentiles_name = "defaultpercentiles"
            cmds = ["percentiles"]
            cmds.extend(["2.5","16","50","84","97.5"])

        if "quartiles" in cmds:
            percentiles_name = "quartiles"
            cmds = ["percentiles"]
            cmds.extend(["25","50","75"])

        if "percentiles" in cmds:

            if percentiles_name is None:
                percentiles_name = "percentiles"
            ndx = cmds.index("percentiles")
            percentiles = cmds[ndx+1:]
            if len(percentiles) == 0:
                print("No percentiles provided. Please provide percentiles as list or use `defaultpercentiles` or `quartiles`")
                sys.exit(1)
            fperc = [float(p) for p in percentiles]

            if not data_already_loaded:
                data = np.load("results.npy")

            axis = None
            if isinstance(axis,basestring) or axis is None:
                axis = (cf.parameter_names+cf.internal_names).index(axis)

            data_percentiles = np.percentile(data, fperc, axis=axis)
            results = {}

            for i, perc in enumerate(percentiles):
                results[perc] = data_percentiles[i]
            np.savez('./results_'+percentiles_name+".npz",**results)



        if not os.path.exists(os.path.join(cwd, "results.p.gz"))\
            and os.path.exists(os.path.join(cwd, "results.p")):
            p = subprocess.Popen(["gzip", "results.p"])
            exit_code = p.wait()
            if exit_code == 1:
                print("error while using gzip results.p")
                sys.exit(1)

    elif cmd in (git_cmds + submit_cmds + prep_cmds + reset_cmds + add_cmds + rm_cmds +\
                 set_cmds + wrap_cmds + status_cmds + ssh_cmds + sftp_cmds + customwrap_cmds +\
                 get_cmds + test_cmds + param_cmds + qstatus_cmds + err_cmds + estimation_cmds):

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

            cf = qconfig(qsuiteparser=qsuiteparser)
            print(type(cf))

            if cmd == "test":

                if len(args)==1:
                    jobid = 0
                    respath = os.path.join(os.getcwd(),".test")
                elif len(args)==2:
                    jobid = int(args[1])
                    respath = os.path.join(os.getcwd(),".test")
                elif len(args)>2:
                    jobid = int(args[1])
                    respath = args[2]

                sys.path.insert(1,os.getcwd()) #add current working directory to import paths
                job(jobid,respath,cf)

            elif cmd == "local":

                N_jobs = cf.get_number_of_jobs()
                jobids = range(N_jobs)
                respath = "current_results"

                def local_job(j_id,N_jobs=None,respath=None,cf=None):
                    print(j_id+1,"/",N_jobs)
                    job(j_id,respath,cf)

                wrap_local(cf)

                sys.path.insert(1,os.getcwd()) #add current working directory to import paths

                if hasattr(cf,"n_local_cpus"):
                    ncpu = cf.n_local_cpus
                else:
                    ncpu = 1

                partial_job = partial(local_job,N_jobs=N_jobs,respath=respath,cf=cf)
                print("Starting local job with", ncpu, "CPUs")
                pool = Pool(ncpu)    
                pool.map(partial_job,jobids)

                from qsuite.queuesys.wrap_results import wrap_results as _wrap
                _wrap(is_local=True,localrespath=respath)

            sys.exit(0)     

        elif cmd in param_cmds:
            cf = qconfig(qsuiteparser=qsuiteparser)
            print_params(cf)

        elif cmd in estimation_cmds:

            if len(args)>1:
                bytestring = args[1]
            else:
                print("No number of bytes per parameter combination given.")
                sys.exit(1)

            cf = qconfig(qsuiteparser=qsuiteparser)

            #get dimensions of the list space
            pdims = [ len(p[1]) for p in cf.external_parameters ]
            idims = [ len(p[1]) for p in cf.internal_parameters ]

            def get_size_string(number_of_bytes):
                if number_of_bytes == 0:
                    return "0B"
                names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                i = int(math.floor(math.log(number_of_bytes, 1024)))
                p = math.pow(1024, i)
                s = round(number_of_bytes / p, 2)
                return "%s %s" % (s, names[i])

            number_of_bytes_per_combination = eval(bytestring)
            result_internal = reduce(operator.mul, idims, 1) * number_of_bytes_per_combination
            number_of_external = reduce(operator.mul, pdims, 1)
            result_external = number_of_external * result_internal

            print("This job will generate {0:d} jobs, each of an estimated size of {1}.".format(number_of_external, get_size_string(result_internal)))
            print("This means that the total size of the generated data will be an estimated {0}".format(get_size_string(result_external)))


        elif cmd in git_cmds + prep_cmds + submit_cmds + wrap_cmds + status_cmds +\
                    ssh_cmds + sftp_cmds + customwrap_cmds + get_cmds + qstatus_cmds + err_cmds:

            cf = qconfig(qsuiteparser=qsuiteparser)
            ssh = ssh_connect(cf)

            # replace directory keyword with path
            for iarg, arg in enumerate(args):
                args[iarg] = args[iarg].replace("DIR",cf.serverpath)
         
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
                    try:
                        array_id = [ int(c) if ("-" not in c) else [ int(rangeid) for rangeid in c.split("-") ] for c in cmds]
                        print("Using array IDs "+str(array_id)+". Beware! Array IDs start counting at 1.")
                    except ValueError:
                        if any([ "err" in c or "wait" in c for c in cmds ]):

                            key_words = []
                            if any([ "err" in c for c in cmds ]):
                                key_words.append("ERR")
                            if any([ "wait" in c for c in cmds ]):
                                key_words.append("WAIT")

                            print("Fetching array IDs that produced errors with keywords", " and ".join(key_words))
                            #print(key_words)
                            progresses = _get_progress_sftp(cf,ssh)
                            array_id = []
                            last_id = 0
                            for j in range(len(cf.parameter_list)):
                                print(j,progresses[j][0].upper())
                                if any( kw in progresses[j][-1].upper() or kw in progresses[j][0].upper() for kw in key_words ):                                    
                                    array_id.append(j+1)

                            print(array_id)
                            if len(array_id)>0:
                                ranges = []
                                for k, g in groupby( enumerate(array_id), lambda IX:IX[0]-IX[1]):
                                    group = list(map(itemgetter(1), g))
                                    if group[0]==group[-1]:
                                        ranges.append(group[0])
                                    else:
                                        ranges.append((group[0], group[-1]))

                                print("Found erros in jobs with Array IDs", ranges)
                                array_id = ranges
                            else:
                                print("No erroneous IDs found.")
                                sys.exit(1)

                        else:
                            print("Unknown submission command",cmds[0],". Aborting.")
                            sys.exit(1)
                else:
                    array_id = None
                    update_git(cf,ssh)

                make_job_ready(cf,ssh,array_id)
                
                if array_id is None:
                    wrap_local(cf)

                start_job(cf,ssh,array_id)

                sys.exit(0)
            elif cmd in wrap_cmds:
                if len(args) == 1:
                    wrap_results(cf,ssh)
                    ssh_command
                elif args[1] == "local":
                    respath = 'current_results'
                    from qsuite.queuesys.wrap_results import wrap_results as _wrap
                    _wrap(is_local=True,localrespath=respath)

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


