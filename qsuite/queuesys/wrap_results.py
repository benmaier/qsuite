from __future__ import print_function
from qconfig import qconfig
from numpy import *
import os
import sys
#import gzip

try:
    # Python 2
    import cPickle as pickle
except ImportError:
    # Python 3
    import pickle

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
        if len(pdims) > 0:
            pcoords = [ [c] for c in list(unravel_index(j, pdims))]
        else:
            pcoords = []

        time = pickle.load(open(cf.resultpath+"/times_%d.p" % j,'rb'))
        if not cf.only_save_times:
            res = pickle.load(open(cf.resultpath+"/results_%d.p" % j,'rb'))
            #print res
            
        for i in range(len(time)):
            if len(idims) > 0:
                icoords = [ [c] for c in list(unravel_index(i, idims)) ]
            else:
                icoords = []
            flat_index = ravel_multi_index(pcoords+icoords,pdims+idims)[0]
            times[flat_index] = time[i]
            if not cf.only_save_times:
                results[flat_index] = res[i]
except Exception as e:
    print("*** Caught exception: %s,%s" % (e.__class__,e))
    print("couldn't load all files")
    sys.exit(1)


#convert to lists for better portability
times = times.reshape(pdims+idims).tolist()
results = results.reshape(pdims+idims).tolist()

try:
    #save the wrapped data
    pickle.dump(times,open(cf.resultpath+"/times.p",'wb'))
    if not cf.only_save_times:
        pickle.dump(results,open(cf.resultpath+"/results.p",'wb'))
except:
    print("couldn't write files")
    sys.exit(1)

    
#delete the original files    
for j in range(cf.jmax+1):
    os.remove(cf.resultpath+"/times_%d.p" % j)
    if not cf.only_save_times:
        os.remove(cf.resultpath+"/results_%d.p" % j)
    
