from __future__ import print_function
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

class _progress_updater():

    def __init__(self):
        self.text = ""

    def update_progress(self,progress, bar_length=40, status=""):        
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
        if text != self.text:
            self.text = text
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

def wrap_results(is_local=False,localrespath="current_results"):

    if not is_local:
        from qconfig import qconfig
    else:
        from qsuite import qconfig

    cf = qconfig()

    if not is_local:
        resultpath = cf.resultpath
        outputpath = resultpath
    else:
        resultpath = os.path.join(os.getcwd(),localrespath)
        outputpath = cf.localpath

    #get dimensions of the list space
    pdims = [ len(p[1]) for p in cf.external_parameters ]
    idims = [ len(p[1]) for p in cf.internal_parameters ]

    #prepare result arrays
    results = empty(pdims+idims,dtype=object).flatten()
    times = empty(pdims+idims,dtype=object).flatten()

    #wrap results of the simulations
    loading_successful = True
    missing_array_ids = []
    updater = _progress_updater()
    for j in range(cf.jmax+1):
        #get coords in list space from linear index
        if len(pdims) > 0:
            pcoords = [ [c] for c in list(unravel_index(j, pdims))]
        else:
            pcoords = []

        if os.path.exists(resultpath+"/times_%d.p" % j) and os.path.exists(resultpath+"/results_%d.p" % j):

            if loading_successful:

                with open(resultpath+"/times_%d.p" % j,'rb') as this_file:
                    time = pickle.load(this_file)

                if not cf.only_save_times:
                    with open(resultpath+"/results_%d.p" % j,'rb') as this_file:
                        res = pickle.load(this_file)
        else:
            if loading_successful:
                print("*** Caught Exception: Files missing! Jobs with the following ARRAY IDs did not produce results:")
            missing_array_ids.append(j+1)
            #print("*** Caught exception: %s,%s" % (e.__class__,e))
            loading_successful = False

                
        if loading_successful:
            for i in range(len(time)):
                if len(idims) > 0:
                    icoords = [ [c] for c in list(unravel_index(i, idims)) ]
                else:
                    icoords = []
                flat_index = ravel_multi_index(pcoords+icoords,pdims+idims)[0]
                times[flat_index] = time[i]
                if not cf.only_save_times:
                    results[flat_index] = res[i]

        updater.update_progress((j+1.)/(cf.jmax+1.))

    if loading_successful:
        # convert to lists for better portability
        times = times.reshape(pdims+idims).tolist()
        results = results.reshape(pdims+idims).tolist()

        try:
            #save the wrapped data
            with open(outputpath+"/times.p",'wb') as dumpfile:
                pickle.dump(times,dumpfile)
            if not cf.only_save_times:
                with open(outputpath+"/results.p",'wb') as dumpfile:
                    pickle.dump(results,dumpfile)
        except Exception as e:
            print("couldn't write files")
            print("Error:",e)
            sys.exit(1)

            
        # delete the original files    
        for j in range(cf.jmax+1):
            os.remove(resultpath+"/times_%d.p" % j)
            if not cf.only_save_times:
                os.remove(resultpath+"/results_%d.p" % j)
    else: 
        i = 0
        missing_array_id_strings = []

        while i < len(missing_array_ids):
            this_id = missing_array_ids[i]
            this_str = str(this_id)
            while i+1 < len(missing_array_ids) and missing_array_ids[i+1] == this_id+1:
                i += 1
                this_id = missing_array_ids[i]

            if (i+1 == len(missing_array_ids) or this_id+1 != missing_array_ids[i+1]) and this_str != str(this_id):
                this_str += '-' + str(this_id)

            missing_array_id_strings.append(this_str)
            i += 1

        print(' '.join(missing_array_id_strings))
        sys.exit(1)

if __name__ == "__main__":
    wrap_results()
