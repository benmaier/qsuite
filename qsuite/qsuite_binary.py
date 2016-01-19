from __future__ import print_function
import os
import sys
import qsuite
from qsuite import qconfig
import ast
from qsuite import get_template_file
from qsuite import copy_template
from qsuite import set_default_file 
from qsuite import get_qsuite
from qsuite import set_in_qsuite
from qsuite import rm_in_qsuite
from qsuite import write_qsuite





def update_git(cf):
    repos = cf.git_repos

    repostring = 'ssh ' + cf.useratserver + ' "'
    for repo in cf.git_repos:
        repostring += "cd %s; git fetch; git pull; %s; " % tuple(repo)

    repostring += '"'
    print(" ===",repostring)
    os.system(repostring)


def init(qsuitefile,opts):
    qsuiteparser = get_qsuite(qsuitefile,init=True)
    copy_template("config",opts)
    copy_template("simulation",opts)
    write_qsuite(qsuiteparser,qsuitefile)


def main():
    
    #create the custom dir if it doesn't exist yet

    if len(sys.argv)==1:
        print("Yes, I'm here! Give me a command!")
        sys.exit(1)

    args = [ a for a in sys.argv[1:] if not a.startswith("-") ]
    opts = [ a for a in sys.argv[1:] if a.startswith("-") ]

    cmd = args[0]
    cwd = os.getcwd()
    qsuitefile = os.path.join(cwd,".qsuite")

    cf = None
    qsuiteparser = None

    if cmd in ["init","initialize"]:
        if len(args)==1:
            if not os.path.exists(qsuitefile):
                init(qsuitefile,opts)
                sys.exit(0)
            else:
                yn = raw_input("There's already a .qsuite file carrying configurations. Do you want to override it (y/n)? ")
                yn = yn.lower()[0]
                if yn == "y":
                    init(qsuitefile,opts)
                sys.exit(0)
        elif len(args)>1:
            if args[1] in ["customwrap", "customwrapper"]:
                copy_template("customwrap",opts)
                sys.exit(0)
            else:
                print("Unknown option",args[1])
                sys.exit(1)

    qsuiteparser = get_qsuite(qsuitefile)

    if cmd in ["set"]:
        if len(args)>1:

            thing_to_set = args[1]
            set_to_thing = args[2]

            if thing_to_set in ["cfg", "config", "configuration"]:
                set_in_qsuite(qsuiteparser,qsuitefile,"config",set_to_thing)
            elif thing_to_set in ["sim", "simulation"]:
                set_in_qsuite(qsuiteparser,qsuitefile,"simulation",set_to_thing)
            elif thing_to_set in ["customwrap", "customwrapper"]:
                set_in_qsuite(qsuiteparser,qsuitefile,"customwrap",set_to_thing)
            elif thing_to_set in ["exec", "execute", "exe"]:
                set_in_qsuite(qsuiteparser,qsuitefile,"exec",set_to_thing)

            elif thing_to_set.startswith("default"):
                if len(args)>2:

                    file_to_set = args[3]

                    if thing_to_set in ["defaultcfg", "defaultconfig", "defaultconfiguration"]:
                        set_default_file("config",file_to_set)
                    elif thing_to_set in ["defaultsim", "defaultsimulation"]:
                        set_default_file("simulation",file_to_set)
                    elif thing_to_set in ["defaultwrap", "defaultcustomwrap", "defaultcustomwrapper"]:
                        set_default_file("customwrap",file_to_set)
                else:
                    print("No default file given.")
                    sys.exit(1)
            else:
                print("Option "+ thing_to_set +" not known.")

        else:
            print("Nothing to set!")
            sys.exit(1)

    elif cmd in ["add"]:

        if len(args)>1:
            thing_to_set = args[1]
            set_in_qsuite(qsuiteparser,qsuitefile,"add",thing_to_set)
            sys.exit(0)
        else:
            print("Nothing to add!")
            sys.exit(1)

    elif cmd in ["rm"]:
        if len(args)>1:
            rm_in_qsuite(qsuiteparser,qsuitefile,args[1])
        else:
            print("Nothing to remove!")
            sys.exit(1)


    configfile = qsuiteparser.get('Files','config')
    if not os.path.exists(configfile):
        configfile = os.path.join(os.getcwd(),configfile)

    cf = qconfig(configfile)

    if cmd in ["git","gitupdate","git_update","updategit","update_git"]:
        update_git()
    else:
        pass


