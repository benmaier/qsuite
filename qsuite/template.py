import shutil
import os
import sys
import qsuite

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



def copy_template(mode):

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
    shutil.copy2(sourcefile,targetfile)



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

    potential_file = os.join(qsuite.customdir,filename)
    copy_file = True

    if os.path.exists(potential_file):
        yn = raw_input("There's already a custom " + mode + " file set. Do you want to override it (y/n)? ")
        yn = yn.lower()[0]
        copy_file = (yn == "y")

    if not os.path.exists(sourcefile):
        sourcefile = os.path.join(os.getcwd(),sourcefile)

    if copy_file:
        shutil.copy2(sourcefile,potential_file)