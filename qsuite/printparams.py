from __future__ import print_function
from tabulate import tabulate
import copy
from qsuite import ssh_command

import tempfile

def _get_progress_fn(cf, j):
    str_len = str(len(str(len(cf.parameter_list)-1)))
    fmt = "%0"+str_len+"d_%d"
    return cf.serverpath + ("/output/progress_"+fmt) % (j, len(cf.parameter_list)-1)


def print_params(cf):

    #for each parameter combination, add job id (j) in the beginning and arrayjob id in the end
    params = [ [j] + list(p) + [j+1] for j,p in enumerate(cf.parameter_list) ]

    #get names from config, besides if the entry is None and the length is equal to the number of measurements, then add MeasID
    names = [ n if not (n is None and len(cf.external_parameters[i][1])==cf.N_measurements) else "Meas.ID" for i,n in enumerate(cf.parameter_names)  ]

    print(tabulate(params, headers=["Job ID"] + names + ["Array ID"]))


def _get_progress_sftp(cf,ssh):

    N = len(cf.parameter_list)-1
    filepath = cf.serverpath + "/output/progress_*_"+str(N)
    cmd = "cd " +cf.serverpath + "/output/; cat progress_*_"+str(N)+" > all_progress" 
    ssh_command(ssh,cmd,noprint=True)

    ftp = ssh.open_sftp()

    with tempfile.TemporaryFile() as tmp:

        ftp.getfo(cf.serverpath + "/output/all_progress", tmp)
        tmp.seek(0)

        progresses_ = [ s.decode('utf-8')[:-1] for s in tmp.readlines() ]
        progresses = []
        for p in progresses_:
            if len(p)>1:
                text_and_time = p.split("__")
                if len(text_and_time)==1:
                    text_and_time.append("")
            else:
                text_and_time = ['waiting...','']

            progresses.append(text_and_time)

    return progresses

def print_status(cf,ssh):

    #for each parameter combination, add job id (j) in the beginning and arrayjob id in the end
    progresses = _get_progress_sftp(cf,ssh)
    prog = []

    record_waiting_id = False
    record_done_id = False

    # go through the progresses and clump together all 'waitings' and 'dones'
    j = 0
    while j<len(progresses):

        # while there's normal entries, count up and add them to output
        while j<len(progresses) and progresses[j][0]!='waiting...' and progresses[j][-1]!="done":
            prog.append( [j+1] + progresses[j] )
            j += 1

        # start clumping 'waitings'
        if j<len(progresses) and progresses[j][0]=='waiting...':

            old_id = j+1

            while j<len(progresses) and progresses[j][0]=='waiting...':
                j += 1

            if old_id==j:
                prog.append( [ old_id ] + progresses[old_id-1])
                #if j<len(progresses):
                #    prog.append( [ j+1 ] + progresses[j])
            else:
                prog.append( [ str(old_id)+"-"+str(j) ] + progresses[j-1])

        # start clumping 'dones'
        if j<len(progresses) and progresses[j][-1]=='done':

            old_id = j+1

            while j<len(progresses) and progresses[j][-1]=='done':
                j += 1

            if old_id==j:
                prog.append( [ old_id ] + progresses[old_id-1])
                #if j<len(progresses):
                #    prog.append( [ j+1 ] + progresses[j])
            else:
                prog.append( [ str(old_id)+"-"+str(j) ] + progresses[j-1])


    #prog = [ [j+1]+p for j,p in enumerate(progresses) ]

    names = [ "Array ID", "Progress", "Rem. Time" ]

    print(tabulate(prog, headers=names))


def print_params_and_status(cf,ssh):
    
    #for each parameter combination, add job id (j) in the beginning and arrayjob id in the end
    progresses = _get_progress_sftp(cf,ssh)
    table = [ [j] + list(p[0]) + [j+1] + list(p[1]) for j,p in enumerate(zip(cf.parameter_list,progresses)) ]

    #get names from config, besides if the entry is None and the length is equal to the number of measurements, then add MeasID
    names = [ n if not (n is None and len(cf.external_parameters[i][1])==cf.N_measurements) else "Meas.ID" for i,n in enumerate(cf.parameter_names)  ]
    names = ["Job ID"] + names + ["Array ID",  "Progress", "Rem. Time" ]

    print(tabulate(table, headers = names))
