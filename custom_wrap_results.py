import config_file as cf
import cPickle as pickle
from numpy import *
import os



#=============================================================================

def mean_and_err(arr,axis="measurements"):

    if isinstance(axis,basestring):
        axis = (cf.parameter_names+cf.internal_names).index(axis)
    else:
        axis = mode

    return arr.mean(axis=axis), arr.std(axis=axis)/sqrt(len(cf.measurements))

#====== definition for the treatment of the results goes here ================= 

def prepare_results(res):
    return mean_and_err(res)

#==============================================================================

times = pickle.load(open(cf.resultpath+"/times.p",'r'))
time,err = mean_and_err(array(times))
savez(cf.path+"/custom_results/mean_err_times.npz",times,err)

if not cf.only_save_times:
    results = pickle.load(open(cf.resultpath+"/results.p",'r'))
    results = prepare_results(array(results))
    if isinstance(results,(list,tuple)):
        savez(cf.path+"/custom_results/mean_err_result_list.npz",*results)
    else:
        save(cf.path+"custom_results/mean_err_results.npy",results)


