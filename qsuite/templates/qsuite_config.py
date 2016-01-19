import os 

#=========== SIMULATION DETAILS ========
projectname = "project"
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
                        ('p3', p3[:1]),
                        ('p3', p4[:]),
                      ]
standard_parameters = [
                        ( 'p5', p5[1] ),
                        ( 'p6', p6[2] ),
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
basename = "experimentname"
name = basename + "_NMEAS_" + str(N_measurements) + "_ONLYSAVETIME_" + str(only_save_times)
pathatserver = "~/" + projectname + "/" + name + "/"
resultpath = pathatserver + "/results"

#=======================================
localdir = os.path.join(os.getcwd(),"results_"+name)

#========================
git_repos = [
                ( "/path/to/repo", "python setup.py install --user" )
            ]


#============ FILES TO COPY TO SERVER =============
scp_files = []
code_after_scp = """ """