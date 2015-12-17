import config_file as cf
import cPickle as pickle

if not cf.only_save_times:
    pass

times = [ None for cf.jmax+1 ]

for j in range(cf.jmax+1):
    times[j] = pickle.load(cf.resultpath+"/times_%d.pickle"%j)

pickle.dump(times,open(cf.resultpath+"/times.pickle"))
