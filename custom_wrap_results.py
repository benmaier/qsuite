import config_file as cf
import cPickle as pickle
from numpy import *
import os

#get dimensions of the list space
pdims = [ len(p) for p in cf.parameter_list ]
idims = [ len(p) for p in cf.internal_parameter_list ]

#prepare result arrays
results = empty(pdims+idims,dtype=object)
times = empty(pdims+idims,dtype=object)

#wrap results of the simulations
for j in range(cf.jmax+1):
    #get coords in list space from linear index
    pcoords = list(unravel_index(j, pdims))
    time = pickle.load(open(cf.resultpath+"/times_%d.pickle" % j,'r'))
    if not cf.only_save_times:
        res = pickle.load(open(cf.resultpath+"/results_%d.pickle" % j,'r'))
        
    for i in range(len(res)):
        icoords = list(unravel_index(i, idims))
        times[pcoords+icoords] = time[i]
        if not cf.only_save_times:
            results[pcoords+icoords] = res[i]

#convert to lists for better portability
times = times.tolist()
results = results.tolist()

#save the wrapped data
pickle.dump(times,open(cf.resultpath+"/times.pickle"),'w')
if not cf.only_save_times:
    pickle.dump(results,open(cf.resultpath+"/results.pickle",'w'))
    
#delete the original files    
for j in range(cf.jmax+1):
    os.remove(cf.resultpath+"/times_%d.pickle" % j)
    if not cf.only_save_times:
        os.remove(cf.resultpath+"/results_%d.pickle" % j)
    
