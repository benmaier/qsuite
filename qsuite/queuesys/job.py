from __future__ import print_function
import sys
import time
import os

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

    #get kwargs for the simulation of this jobnumber
    job_kwargs = cf.get_kwargs(cf.parameter_names,cf.parameter_list[j])

    #prepare result lists
    results = [ None for i in range(len(cf.internal_parameter_list)) ]
    times = list(results) #copy

    N_int_param = len(results)

    #loop through the internal args
    for ip,internal_params in enumerate(cf.internal_parameter_list):

        #wrap all kwargs necessary for the simulation
        kwargs = cf.get_kwargs(cf.internal_names,cf.internal_parameter_list[ip])
        kwargs.update(job_kwargs)
        kwargs.update(cf.std_kwargs)

        #add seed
        if cf.seed>=0:
            key = 'seed'
            if key in kwargs:
                key = 'randomseed'
            kwargs[key] = N_int_param*j + ip + cf.seed
        
        t_start = time.time()

        #start the simulation and save the result
        results[ip] = simcode.simulation_code(kwargs)

        t_end = time.time()
        
        times[ip] = t_end - t_start
        
    #save results
    if not os.path.exists(cf.resultpath):
        os.mkdir(cf.resultpath)

    if any([result is not None for result in results]) and not cf.only_save_times:
        pickle.dump(results,open(cf.resultpath+'/results_%d.p' % (j),'wb'),protocol=pickle.HIGHEST_PROTOCOL)

    #save times needed
    pickle.dump(times,open(cf.resultpath+'/times_%d.p' % (j),'wb'),protocol=pickle.HIGHEST_PROTOCOL)


if __name__=="__main__":

    #get job number and alternatively another resultpath
    args = sys.argv[1:]
    j = int(args[0]) #jobnumber
    if len(args)>1:
        resultpath = args[1] 
    else:
        resultpath = None

    job(j,resultpath)
