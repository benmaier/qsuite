#============================== DEFINITIONS ============================
SHELL=/bin/bash

BASENAME=symbSSA
NMEASUREMENTS=10
PRIORITY=1
ONLYSAVETIME=False

NAME=$(BASENAME)_NMEAS_$(NMEAS)_ONLYSAVETIME_$(ONLYSAVETIME)
WDPATH=/home/bfmaier/SSA_symbiosis_fluctuating_fitness/$(NAME)
LOCALDIR=$(NAME)

USERATSERVER=bfmaier@groot0.biologie.hu-berlin.de
PYTHONPATH=/usr/local/bin/python2.7
MEMORY=2G

PARAMLISTSTRING="\[alpha\,\ measurements\]"
INTERNALLISTSTRING="\[Nmax\[\:5\]\]"
STANDARDLISTSTRING="\[corr_matrices\[0\],\ y0\[4\]\]"
GITREPOS="/home/bfmaier/tau-leaping-for-evolution"


#============================== FILENAMES ==============================

cfg:
	sed "s#NMEASUREMENTS#$(NMEASUREMENTS)#g" < config_dummy.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#MEMORY#$(MEMORY)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#PYTHONPATH#$(PYTHONPATH)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#WDPATH#$(WDPATH)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#PARAMLISTSTRING#$(PARAMLISTSTRING)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#INTERNALLISTSTRING#$(INTERNALLISTSTRING)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#STANDARDLISTSTRING#$(STANDARDLISTSTRING)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#ONLYSAVETIME#$(ONLYSAVETIME)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py

status:
	ssh $(USERATSERVER) "qstat"

statusall:
	ssh $(USERATSERVER) "qstat -u \"*\""

gitupdateserver:
	python update_git_repos_server.py $(PYTHONPATH) $(USERATSERVER) $(GITREPOS)

job:
	make cfg
	make jobfile
	make wrap_every
	ssh $(USERATSERVER) "rm -r $(FOLDER)/jobscripts; mkdir -p $(FOLDER)"
	scp -r \
			symbiosis_sim.py\
			fluctuating_growth_simulator.py\
			config_file.py\
			wrapper_for_cluster.py \
			make_and_submit_jobs.sh \
		$(USERATSERVER):$(FOLDER)
	ssh $(USERATSERVER) "\
			cd $(FOLDER);\
		    ls;\
			chmod +x ./make_and_submit_jobs.sh;\
			./make_and_submit_jobs.sh"

get_results:
	ssh $(USERATSERVER) "cd $(FOLDER); /usr/local/bin/python2.7 wrapper_for_cluster.py"
	#make wrap_every
	scp $(USERATSERVER):$(FOLDER)/*.p $(LOCALDIR)
	#scp $(USERATSERVER):$(FOLDER)/wrapper* .

wrap_every:
	mkdir -p $(LOCALDIR)
	cp \
			symbiosis_sim.py\
			fluctuating_growth_simulator.py\
			config_file.py\
			wrapper_for_cluster.py \
			make_and_submit_jobs.sh\
	 $(LOCALDIR)/

clean:
	rm -rf *# *~ ./jobscripts/*
