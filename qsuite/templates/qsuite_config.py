import os 

#=========== SIMULATION DETAILS ========
projectname = "project"
basename = "experimentname"

seed = -1
N_measurements = 1

measurements = range(N_measurements)
params1 = range(3)
params2 = range(3)
params3 = range(3)
params4 = range(3)
params5 = range(3)
params6 = range(3)

external_parameters = [
                        ( 'p1', params1[:2]   ),
                        ( 'p2', params2       ),
                        ( None   , measurements ),
                      ]
internal_parameters = [
                        ('p3', params3[:1]),
                        ('p3', params4[:]),
                      ]
standard_parameters = [
                        ( 'p5', params5[1] ),
                        ( 'p6', params6[2] ),
                      ]

only_save_times = False

#============== QUEUE ==================
queue = "SGE"
memory = "1G"
priority = 0

#============ CLUSTER SETTINGS ============
username = "user"
server = "localhost"
useratserver = username + u'@' + server

shell = "/bin/bash"
pythonpath = "python"
name = basename + "_NMEAS_" + str(N_measurements) + "_ONLYSAVETIME_" + str(only_save_times)
serverpath = "/home/"+username +"/"+ projectname + "/" + name 
resultpath = serverpath + "/results"

#============== LOCAL SETTINGS ============
localpath = os.path.join(os.getcwd(),"results_"+name)
n_local_cpus = 1

#========================
git_repos = [
                ( "/path/to/repo", pythonpath + " setup.py install --user" )
            ]

