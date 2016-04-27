from __future__ import print_function
import shutil
import os
import sys
import qsuite
from qsuite import rm

if sys.version_info[0] == 2:
    pass
elif sys.version_info[0] == 3:
    raw_input = input
else:
    print("Python version",sys.version_info[0],"not supported")
    sys.exit(1)

def mkdirp_customdir():
    if not os.path.exists(qsuite.customdir):
        os.makedirs(qsuite.customdir)

def get_template_file(filename):

    #check if there exists a custom template
    potential_file = os.path.join(qsuite.customdir,filename)
    if os.path.exists(potential_file):
        sourcefile = potential_file
    else:
        sourcefile = os.path.join(qsuite.__path__[0],"templates",filename)

    return sourcefile

def reset(mode):

    if mode == "config":
        filename = "qsuite_config.py"
    elif mode == "simulation":
        filename = "simulation.py"
    elif mode == "customwrap":
        filename = "custom_wrap_results.py"
    else:
        print("copy_template(): no such mode as", mode)
        sys.exit(1)

    targetfile = os.path.join(qsuite.customdir,filename)

    if os.path.exists(targetfile):
        yn = raw_input("This action deletes the current default "+mode+" file. Do you want to proceed (y/n)? ")
        yn = yn.lower()[0]
        delete_file = (yn == "y")
        if delete_file:
            qsuite.rm(targetfile)


def copy_template(mode,options=[]):

    if mode == "config":
        filename = "qsuite_config.py"
    elif mode == "simulation":
        filename = "simulation.py"
    elif mode == "customwrap":
        filename = "custom_wrap_results.py"
    else:
        print("copy_template(): no such mode as", mode)
        sys.exit(1)

    sourcefile = get_template_file(filename)

    #target file is the current working directory
    targetfile = os.path.join(os.getcwd(),filename)

    #copy template to cwd
    if not os.path.exists(targetfile) or "-f" in options:
        shutil.copy2(sourcefile,targetfile)

        if targetfile.endswith(".py"):
            rm(targetfile+"c") #remove class files

        print("Initialized",mode,"as",filename)
    else:
        print("The file",filename,"already exists. Remove it first or use the '-f' flag to force copying the template.")




def set_default_file(mode,sourcefile):

    if mode == "config":
        filename = "qsuite_config.py"
    elif mode == "simulation":
        filename = "simulation.py"
    elif mode == "customwrap":
        filename = "custom_wrap_results.py"
    else:
        print("copy_template(): no such mode as", mode)
        sys.exit(1)

    mkdirp_customdir()

    potential_file = os.path.join(qsuite.customdir,filename)
    copy_file = True

    if os.path.exists(potential_file):
        yn = raw_input("There's already a custom " + mode + " file set. Do you want to override it (y/n)? ")
        yn = yn.lower()[0]
        copy_file = (yn == "y")

    if not os.path.exists(sourcefile):
        sourcefile = os.path.join(os.getcwd(),sourcefile)

    if copy_file:
        shutil.copy2(sourcefile,potential_file)
