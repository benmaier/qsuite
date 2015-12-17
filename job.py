import config_file as cf
import sys
import time
import cPickle as pickle
import simulation as simcode
from itertools import izip

#get job number and alternatively another resultpath
args = sys.argv[1:]
j = int(args[0]) #jobnumber
if len(args)>1:
    cf.resultpath = args[1] 

#get kwargs for the simulation of this jobnumber
if not (len(parameter_names)==1 and parameter_names[0]==''):
    job_kwargs = { cf.name_to_option[name]:parameter_list[j][iname] for iname,name in izip(xrange(len(parameter_names)),cf.parameter_names) }
else:
    job_kwargs = {}

#prepare result lists
results = [ None for i in xrange(len(cf.internal_parameter_list)) ]
times = results.copy()

#loop through the internal args
for internal_params in cf.internal_parameter_list:

    #wrap all kwargs necessary for the simulation
    if not (len(internal_names)==1 and internal_names[0]==''):
        kwargs = { cf.name_to_option[name]:internal_params[iname] for iname,name in izip(xrange(len(internal_names)),cf.internal_names) }
    else:
        kwargs = {}
    kwargs.update(job_kwargs)
    kwargs.update(cf.std_kwargs)

    t_start = time.time()

    #start the simulation and save the result
    results[ip] = simcode.simulation_code(kwargs)

    t_end = time.time()
    
    times[ip] = t_end - t_start
    
#save results
if any([result is not None for result in results]) and not cf.only_save_times:
    pickle.dump(results,open(cf.resultpath+'/results_%d.pickle' % (j),'w'),protocol=pickle.HIGHEST_PROTOCOL)

#save times needed
pickle.dump(times,open(cf.resultpath+'/times_%d.pickle' % (j),'w'),protocol=pickle.HIGHEST_PROTOCOL)
