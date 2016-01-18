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
        config.set('Files','additional_files',[])
        config.set('Files','execute_after_scp',None)
        write_qsuite(config,qsuitefile)
    else:
        config = cp.RawConfigParser()
        config.read(qsuitefile)

    return config



def write_qsuite(qsuiteparser,qsuitefile):
    qsuiteparser.write(open(qsuitefile,'wb'))
