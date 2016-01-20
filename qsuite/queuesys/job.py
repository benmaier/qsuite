from qconfig import qconfig
import sys
import time
import cPickle as pickle
import simulation as simcode
from itertools import izip

#load configuration
cf = qconfig()

#get job number and alternatively another resultpath
args = sys.argv[1:]
j = int(args[0]) #jobnumber
if len(args)>1:
    cf.resultpath = args[1] 

#get kwargs for the simulation of this jobnumber
job_kwargs = cf.get_kwargs(cf.parameter_names,cf.parameter_list[j])

#prepare result lists
results = [ None for i in xrange(len(cf.internal_parameter_list)) ]
times = list(results) #copy

#loop through the internal args
for ip,internal_params in izip(xrange(len(cf.internal_parameter_list)),cf.internal_parameter_list):

    #wrap all kwargs necessary for the simulation
    kwargs = cf.get_kwargs(cf.internal_names,cf.internal_parameter_list[ip])
    kwargs.update(job_kwargs)
    kwargs.update(cf.std_kwargs)
    
    t_start = time.time()

    #start the simulation and save the result
    results[ip] = simcode.simulation_code(kwargs)

    t_end = time.time()
    
    times[ip] = t_end - t_start
    
#save results
if any([result is not None for result in results]) and not cf.only_save_times:
    pickle.dump(results,open(cf.resultpath+'/results_%d.p' % (j),'w'),protocol=pickle.HIGHEST_PROTOCOL)

#save times needed
pickle.dump(times,open(cf.resultpath+'/times_%d.p' % (j),'w'),protocol=pickle.HIGHEST_PROTOCOL)
