from __future__ import print_function
import os 
import sys
import numpy as np
import ast
import itertools

try:
    # Python 2
    from itertools import izip
except ImportError:
    # Python 3
    izip = zip

class qconfig(object):

    def __init__(self,filename="qsuite_config.py",qsuiteparser=None):

        if qsuiteparser is None:
            self.configpath = os.path.join(os.getcwd(), filename)
        else:
            self.configfile = qsuiteparser.get('Files','config')
            if not os.path.exists(self.configfile):
                self.configfile = os.path.join(os.getcwd(),self.configfile)

            self.files_to_scp = { 
                                    "qsuite_config.py": self.configfile,
                                    "simulation.py": qsuiteparser.get('Files','simulation'),
                                }

            if not qsuiteparser.get('Files','execute_after_scp') == "None": 
                self.files_to_scp["execute_after_scp.sh"] = qsuiteparser.get('Files','execute_after_scp')

            if not qsuiteparser.get('Files','customwrap') == "None":
                self.files_to_scp["custom_wrap_results.py"] = qsuiteparser.get('Files','customwrap')

            add_files = ast.literal_eval(qsuiteparser.get('Files','additional_files'))
            self.additional_files_to_scp = [ f for f in add_files if not f=='' ]

            self.configpath = self.configfile



        if os.path.exists(self.configpath):
            cf = self.get_cf(self.configpath)
        else:
            print("No "+filename+" found in current working directory!")
            sys.exit(1)


        #inherit all properties from the config module
        self.inherit_properties(cf)

        #prepare parameters lists
        self.parameter_names, self.parameter_list = self.get_param_lists(self.external_parameters)
        self.internal_names, self.internal_parameter_list = self.get_param_lists(self.internal_parameters)

        #prepare standard parameters list and kwargs
        self.standard_names, self.standard_list = self.get_param_lists(self.standard_parameters,product=False)
        self.std_kwargs = self.get_kwargs(self.standard_names,self.standard_list)

        #get min and max jobnumber
        self.jmin = 0
        self.jmax = len(self.parameter_list)-1

    #======================== INHERIT PROPERTIES FROM THE CONFIG FILE ============================

    def get_cf(self,path):

        if sys.version_info[0] == 2:
            import imp
            cf = imp.load_source("queueconfig",path)
        elif sys.version_info >= (3,5):
            import importlib.util
            specifications = importlib.util.spec_from_file_location("queueconfig",path)
            cf = importlib.util.module_from_spec(specifications)
            specifications.loader.exec_module(cf)
        else:
            print("Python version",sys.version_info[0],"not supported")
            sys.exit(1)

        return cf

    def inherit_properties(self,cf):
        new_props = [ prop for prop in dir(cf) if not prop.startswith('__') ]

        for p in new_props:
            self.__dict__[p] = cf.__dict__[p]

    #============================= PARAMETER STRING CONVERSION FUNCTIONS ==========================

    """
    def get_param_lists_old(self,pliststr,plist=None):
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

    def get_kwargs_old(self,plist,pnames,name_to_option):
        if not (len(pnames)==1 and pnames[0]==""):
            kwargs = { 
                       name_to_option[name]:plist[iname]\
                       for iname,name in itertools.izip(range(len(pnames)),pnames)\
                       if name_to_option[name] is not None 
                     }
        else:
            kwargs = {}

        return kwargs
    """

    def get_param_lists(self,plist,product=True):
        pnames = [ p[0] for p in plist ]
        plist = [ p[1] for p in plist ]

        if product:
            parameter_list = list(itertools.product(*plist))
        else:
            parameter_list = plist

        return pnames, parameter_list

    def get_kwargs(self,pnames,current_parameters):
        kwargs = { 
                   name : current_parameters[iname]\
                   for iname,name in izip(range(len(pnames)),pnames)\
                   if name is not None 
                 }

        return kwargs

    def get_number_of_jobs(self):
        return len(self.parameter_list)

    
if __name__=="__main__":

    cf = qconfig()

    print(cf.get_param_lists(cf.parameter_names,cf.parameter_list[0]))
    
