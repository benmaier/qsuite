from numpy import *
from itertools import izip
import itertools
import re
import sys

#==================================== SIMULATION SPECIFIC DETAILS ============================
#declare parameters
params0 = arange(10)
params1 = arange(10)
params2 = arange(10)
params3 = arange(10)
params4 = arange(10)
params5 = arange(10)
measurements = arange(NMEASUREMENTS)


#dict mapping the name of an array above to the option name needed in "simulation.py"
name_to_option = { 
                   "params0": "parameter_0",
                   "params1": "parameter_1",
                   "params2": "parameter_2",
                   "params3": "parameter_3",
                   "params4": "parameter_4",
                   "params5": "parameter_5",
                   "measurements": None, #this is not going to be converted to a keyword argument
                 }
#============================= PARAMETER STRING CONVERSION FUNCTIONS ==========================

def get_param_lists(pliststr,plist=None):
    if pliststr[-1]=="]" and pliststr[0]=="[":
        try:
            pstring = pliststr[1:-1] #delete first and last character
            array_names = re.sub("[\(\[].*?[\)\]]", "", pstring) #delete array delimiters and what's in between them
            array_names = re.sub(" ", "", array_names).split(',') #delete spaces and get list
            if plist is not None:
                parameter_list = list(itertools.product(*plist))
        except:
            print "wrong format in parameter list:", pliststr
            sys.exit(1)
    else:
        print "wrong format in outer scope of parameter list:", pliststr
        print "forgot the mandatory brackets around the arrays: [] ?)"
        sys.exit(1)

    if plist is not None:
        return array_names, parameter_list
    else:
        return array_names

def get_kwargs(plist,pnames,name_to_option):
    if not (len(pnames)==1 and pnames[0]==""):
        kwargs = { 
                   name_to_option[name]:plist[iname]\
                   for iname,name in itertools.izip(range(len(pnames)),pnames)\
                   if name_to_option[name] is not None 
                 }
    else:
        kwargs = {}

    return kwargs

#============================== GENERAL CONFIGS =================================

#set memory and seed for RNG
memory = "MEMORY"
seed = "SEED"

#set paths
pythonpath = "PYTHONPATH"
path = "WDPATH"
resultpath = path+"/results"
name = "NAME"

#set queueing architecture
queue = "QUEUESYS"

#set parameter settings
#which parameters are taken care of on the cluster
pliststr = "PARAMLISTSTRING"
plist = PARAMLISTSTRING
#which parameters are taken care of internally (per job)
iliststr = "INTERNALLISTSTRING"
ilist = INTERNALLISTSTRING
#which parameters are the same for every job
sliststr = "STANDARDLISTSTRING"
slist = STANDARDLISTSTRING

#prepare for job.py
parameter_names,parameter_list = get_param_lists(pliststr,plist)
internal_names,internal_parameter_list = get_param_lists(iliststr,ilist)

#prepare standard kwargs
standard_names = get_param_lists(sliststr)
std_kwargs = get_kwargs(slist,standard_names,name_to_option)

#get min and max jobnumber
jmin = 0
jmax = len(parameter_list)-1

#Sometimes one prefers to just measure the time of one simulation
only_save_times = ONLYSAVETIME


if __name__=="__main__":
    print "parameter_list =",parameter_list
    print "internal_parameter_list =",internal_parameter_list
    print "std_kwargs =",std_kwargs
