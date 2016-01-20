from qconfig import qconfig
import cPickle as pickle
from numpy import *
import os
import sys

cf = qconfig()

#get dimensions of the list space
pdims = [ len(p[1]) for p in cf.external_parameters ]
idims = [ len(p[1]) for p in cf.internal_parameters ]

#prepare result arrays
results = empty(pdims+idims,dtype=object).flatten()
times = empty(pdims+idims,dtype=object).flatten()

try:
    #wrap results of the simulations
    for j in range(cf.jmax+1):
        #get coords in list space from linear index
        pcoords = [ [c] for c in list(unravel_index(j, pdims))]

        time = pickle.load(open(cf.resultpath+"/times_%d.p" % j,'r'))
        if not cf.only_save_times:
            res = pickle.load(open(cf.resultpath+"/results_%d.p" % j,'r'))
            #print res
            
        for i in range(len(res)):
            icoords = [ [c] for c in list(unravel_index(i, idims)) ]
            flat_index = ravel_multi_index(pcoords+icoords,pdims+idims)
            times[flat_index] = time[i]
            if not cf.only_save_times:
                results[flat_index] = res[i]
except:
    print "couldn't load all files"
    sys.exit(1)

#convert to lists for better portability
times = times.reshape(pdims+idims).tolist()
results = results.reshape(pdims+idims).tolist()

try:
    #save the wrapped data
    pickle.dump(times,open(cf.resultpath+"/times.p",'w'))
    if not cf.only_save_times:
        pickle.dump(results,open(cf.resultpath+"/results.p",'w'))
except:
    print "couldn't write files"
    sys.exit(1)
    
#delete the original files    
for j in range(cf.jmax+1):
    os.remove(cf.resultpath+"/times_%d.p" % j)
    if not cf.only_save_times:
        os.remove(cf.resultpath+"/results_%d.p" % j)
    
