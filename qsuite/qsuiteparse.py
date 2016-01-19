import sys
import qsuite

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

    if os.path.exists(set_to_thing):
        if mode == "add":
            add_files = ast.literal_eval(qsuiteparser.get('Files','additional_files'))

            if add_files[0] == ['']:
                add_files.pop(0)    

            add_files.append(set_to_thing)
            set_to_thing = add_files

        qsuiteparser.set('Files',opt,set_to_thing)
        write_qsuite(qsuiteparser,qsuitefile)
    else:
        print("File",set_to_thing,"does not exist")
        sys.exit(1)

def rm_in_qsuite(qsuiteparser,qsuitefile,thing_to_rm):
    add_files = ast.literal_eval(qsuiteparser.get('Files','additional_files'))
    exec_file = qsuiteparser.get('Files','execute_after_scp')

    changed = False

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

    if changed:
        write_qsuite(qsuiteparser,qsuitefile)

def write_qsuite(qsuiteparser,qsuitefile):
    qsuiteparser.write(open(qsuitefile,'wb'))
