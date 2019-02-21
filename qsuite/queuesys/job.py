from __future__ import print_function
import sys
import time
import os
import traceback

from numpy import mean
from numpy import std
from numpy import sqrt

try:
    # Python 2
    from itertools import izip
    import cPickle as pickle
except ImportError:
    # Python 3
    import pickle
    izip = zip

if os.path.exists("./qconfig.py"):
    from qconfig import qconfig
else:
    from qsuite import qconfig

def _get_progress_fn(cf, j):
    str_len = str(len(str(len(cf.parameter_list)-1)))
    fmt = "%0"+str_len+"d_%d"
    return cf.serverpath + ("/output/progress_"+fmt) % (j, len(cf.parameter_list)-1)

def _update_progress(progress, bar_length=40, status=""):        
        """
        This function was coded by Marc Wiedermann (https://github.com/marcwie)

        Draw a progressbar according to the actual progress of a calculation.

        Call this function again to update the progressbar.

        :type progress: number (float)
        :arg  progress: Percentile of progress of a current calculation.

        :type bar_length: number (int)
        :arg  bar_length: The length of the bar in the commandline.

        :type status: str
        :arg  status: A message to print behing the progressbar.
        """
        block = int(round(bar_length*progress))
        text = "\r[{0}] {1:4.1f}% {2}".format("="*block + " "*(bar_length-block),
                                         round(progress, 3)*100, status)
        sys.stdout.write(text)
        sys.stdout.flush()
        if progress >= 1:
            sys.stdout.write("\n")

def _get_timeleft_string(t):
    d, remainder = divmod(t,24*60*60)
    h, remainder = divmod(remainder,60*60)
    m, s = divmod(remainder,60)
    t = [d,h,m,s]
    t_str = ["%dd", "%dh", "%dm", "%ds"]
    it = 0 
    while it<4 and t[it]==0.:
        it += 1
    text = (" ".join(t_str[it:it+2])) % tuple(t[it:it+2])
    return text
    

def _update_progress_file(progress_id, N_id, times, filename, bar_length=40):

    progress = (progress_id+1.) / float(N_id)
    block = int(round(bar_length*progress))
    if progress_id==N_id-1:
        timeleft = "done"
    elif len(times)>0:
        timeleft = int((N_id-progress_id-1) * mean(times))
        timeleft = _get_timeleft_string(timeleft)
    else:
        timeleft = "no estimate yet"
    
    text = "[{0}] {1:4.1f}%__{2}\n".format("="*block + " "*(bar_length-block),
                                     round(progress, 3)*100, timeleft)

    progressfile = open(filename,"w")
    progressfile.write(text)
    progressfile.close()

def job(j,resultpath=None,cf=None):

    is_local = cf is not None

    if not is_local:
        cf = qconfig()

    #get the resultpath from arguments
    #if no resultpath is given, it is assumed that a local simulation takes place
    if is_local:
        cf.resultpath = resultpath
        simcode_path = os.path.join(os.getcwd(),cf.files_to_scp["simulation.py"])
    else:
        simcode_path = os.path.join(os.getcwd(),"simulation.py")

    if not os.path.exists(simcode_path):
        print("No simulation file provided!")


    #import the simulation module
    try:
        if sys.version_info[0] == 2:
            import imp
            simcode = imp.load_source("sim",simcode_path)
        elif sys.version_info >= (3,5):
            import importlib.util
            specifications = importlib.util.spec_from_file_location("sim",simcode_path)
            simcode = importlib.util.module_from_spec(specifications)
            specifications.loader.exec_module(simcode)
        else:
            print("Python version",sys.version_info[0],"not supported.")
            sys.exit(1)
    except Exception as e:
        # in case there's an error, write that into the progress file
        if not is_local:
            with open(_get_progress_fn(cf,j),"w") as progressfile:
                progressfile.write("error: "+e.__class__.__name__+"\n")

        traceback.print_exc(file=sys.stderr)
        sys.exit(1) 

    #get kwargs for the simulation of this jobnumber
    job_kwargs = cf.get_kwargs(cf.parameter_names,cf.parameter_list[j])

    #prepare result lists
    results = [ None for i in range(len(cf.internal_parameter_list)) ]
    times = list(results) #copy

    N_int_param = len(results)

    #loop through the internal args
    for ip,internal_params in enumerate(cf.internal_parameter_list):

        #if this is the first run, initiate the progress bar
        if not is_local and ip==0:
            _update_progress_file(ip-1,N_int_param,[],_get_progress_fn(cf,j))

        #wrap all kwargs necessary for the simulation
        kwargs = cf.get_kwargs(cf.internal_names,cf.internal_parameter_list[ip])
        kwargs.update(job_kwargs)
        kwargs.update(cf.std_kwargs)

        #add seed
        if hasattr(cf,'seed') and cf.seed is not None and cf.seed>=0:
            key = 'seed'
            if key in kwargs:
                key = 'randomseed'
            kwargs[key] = N_int_param*j + ip + cf.seed
        
        t_start = time.time()

        try:
            # start the simulation and save the result
            results[ip] = simcode.simulation_code(kwargs)
        except Exception as e:
            # in case there's an error, write that into the progress file
            if not is_local:
                with open(_get_progress_fn(cf,j),"w") as progressfile:
                    progressfile.write("error: "+e.__class__.__name__+"\n")

            traceback.print_exc(file=sys.stderr)
            sys.exit(1) 

        t_end = time.time()
        
        times[ip] = t_end - t_start

        if is_local:
            if ip>0:
                _update_progress((ip + 1.)/N_int_param,40,"est. time per measurement: "+ str(mean(times[:ip+1])) + " +/- " + str(std(times[:ip+1])/sqrt(ip+1)) )
            else:
                _update_progress((ip + 1.)/N_int_param,40,"est. time per measurement: "+ str(mean(times[:ip+1])) )
        else:
            _update_progress_file(ip,N_int_param,times[:ip+1],_get_progress_fn(cf,j))
        
    #save results
    if not os.path.exists(cf.resultpath):
        os.mkdir(cf.resultpath)

    if any([result is not None for result in results]) and not cf.only_save_times:
        with open(cf.resultpath+'/results_%d.p' % (j),'wb') as dumpfile:
            pickle.dump(results,dumpfile,protocol=pickle.HIGHEST_PROTOCOL)

    #save times needed
    with open(cf.resultpath+'/times_%d.p' % (j),'wb') as dumpfile:
        pickle.dump(times,dumpfile,protocol=pickle.HIGHEST_PROTOCOL)


if __name__=="__main__":

    #get job number and alternatively another resultpath
    args = sys.argv[1:]
    j = int(args[0]) #jobnumber
    if len(args)>1:
        resultpath = args[1] 
    else:
        resultpath = None

    job(j,resultpath)
