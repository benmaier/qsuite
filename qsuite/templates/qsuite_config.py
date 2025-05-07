import os 

#=========== SIMULATION DETAILS ========
projectname = "project"
basename = "experimentname"

seed = -1
N_measurements = 1
save_each_run = False

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

#============== QUEUE =============================================
#=============== set queing system used at your server          ===
#=============== queue can be one of ['PBS', 'SGE', 'SLURM']    ===
queue = "SLURM"
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

#============ CLUSTER PREPARATION ==================================================
#======  bash code loading modules to enable python:                      ==========
#======  e.g. "ml purge; ml +development/24.04 +GCCcore/13.3.0 +Python"   ==========
server_cmds = " "


#============== LOCAL SETTINGS ============
localpath = os.path.join(os.getcwd(),"results_"+name)
n_local_cpus = 1

#============= GIT SETTINGS     ============
git_repos = [
                ( "/path/to/repo", server_cmds + "; " + pythonpath + " -m pip install -e . --user" )
            ]