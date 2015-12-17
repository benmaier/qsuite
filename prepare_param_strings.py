#from config_file import *
import itertools
import re
import sys


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


"""
pliststr = "PARAMLISTSTRING"
plist = PARAMLISTSTRING
iliststr = "INTERNALLISTSTR"
ilist = INTERNALLISTSTR

parameter_list,parameter_names = get_param_list(pliststr,plist)
internal_parameter_list,internal_names = get_param_list(iliststr,ilist)

#parameter_list = zip(range(len(parameter_list)),parameter_list)
"""

if __name__=="__main__":
    arg0 = range(2)
    arg1 = range(3)
    arg2 = range(4)

    pstr1 = "[arg0,arg1,arg2[2:4]]"
    p1 = [arg0,arg1,arg2[2:4]]
    istr1 = "[]"
    i1 = []

    print get_param_lists(pstr1,p1)
    print get_param_lists(istr1,i1)
