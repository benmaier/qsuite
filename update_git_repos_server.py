import os
import sys

pythonpath = sys.argv[1]
useratserver = sys.argv[2]
repos = sys.argv[3:]

repostring = 'ssh ' + useratserver + ' "'
for repo in repos:
    repostring += "cd %s; git fetch; git pull; %s setup.py install --user;" % (repo,pythonpath)

repostring += '"'
print "===",repostring
os.system(repostring)
