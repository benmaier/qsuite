from __future__ import print_function
from tabulate import tabulate
import copy

def print_params(cf):

    #for each parameter combination, add job id (j) in the beginning and arrayjob id in the end
    params = [ [i] + list(p) + [i+1] for i,p in enumerate(cf.parameter_list) ]

    #get names from config, besides if the entry is None and the length is equal to the number of measurements, then add MeasID
    names = [ n if not (n is None and len(cf.external_parameters[i][1])==cf.N_measurements) else "Meas.ID" for i,n in enumerate(cf.parameter_names)  ]

    print(tabulate(params, headers=["Job ID"] + names + ["Array ID"]))
