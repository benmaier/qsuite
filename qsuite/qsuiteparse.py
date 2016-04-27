from __future__ import print_function
import sys
import qsuite
import os
import ast

if sys.version_info[0] == 2:
    import ConfigParser as cp
elif sys.version_info[0] == 3:
    import configparser as cp
else:
    print("Python version",sys.version_info[0],"not supported")
    sys.exit(1)

def get_qsuite(qsuitefile,init=False):

    if init:
        config = cp.RawConfigParser()
        config.add_section('Files')
        config.set('Files','config','qsuite_config.py')
        config.set('Files','simulation','simulation.py')
        config.set('Files','customwrap',None)
        config.set('Files','additional_files',[''])
        config.set('Files','execute_after_scp',None)
        write_qsuite(config,qsuitefile)
    else:
        config = cp.RawConfigParser()
        config.read(qsuitefile)

    return config

def set_in_qsuite(qsuiteparser,qsuitefile,mode,set_to_thing):

    if mode == 'config' or mode == 'simulation' or mode == 'customwrap':
        opt = mode
    elif mode == 'add':
        opt = "additional_files"
    elif mode == 'exec':
        opt = "execute_after_scp"
    else:
        print("Unkown mode:",mode)
        sys.exit(1)

    if type(set_to_thing) in [list,tuple]:
        stuff_exists = True
        for fname in set_to_thing:
            this_exists = os.path.exists(fname)
            stuff_exists = stuff_exists and this_exists
            if not this_exists:
                print("File", set_to_thing,"doesn't exist.")
        if not stuff_exists:
            sys.exit(1)
    else:
        stuff_exists = os.path.exists(set_to_thing)

    if stuff_exists:
        if mode == "add":
            add_files = ast.literal_eval(qsuiteparser.get('Files','additional_files'))

            if add_files[0] == '':
                add_files.pop(0)    

            add_files.extend(set_to_thing)
            add_files = list(set(add_files))
            set_to_thing = add_files

        qsuiteparser.set('Files',opt,set_to_thing)
        write_qsuite(qsuiteparser,qsuitefile)
    else:
        print("File",set_to_thing,"does not exist")
        sys.exit(1)

def rm_in_qsuite(qsuiteparser,qsuitefile,things_to_rm):
    add_files = ast.literal_eval(qsuiteparser.get('Files','additional_files'))
    exec_file = qsuiteparser.get('Files','execute_after_scp')
    custom_file = qsuiteparser.get('Files','customwrap')

    changed = False
    
    for thing_to_rm in things_to_rm: 
        if thing_to_rm in add_files:
            ndx = add_files.index(thing_to_rm)
            add_files.pop(add_files.index(thing_to_rm))
            if len(add_files)==0:
                add_files.append('')
            qsuiteparser.set('Files','additional_files',add_files)
            changed = True

        if thing_to_rm == exec_file:
            qsuiteparser.set('Files','execute_after_scp',None)
            changed = True

        if thing_to_rm == custom_file:
            qsuiteparser.set('Files','customwrap',None)
            changed = True

    if changed:
        write_qsuite(qsuiteparser,qsuitefile)

def write_qsuite(qsuiteparser,qsuitefile):
    qsuiteparser.write(open(qsuitefile,'w'))
