#============================== DEFINITIONS ============================
SHELL=/bin/bash

BASENAME=symbSSA
NMEASUREMENTS=10
PRIORITY=1
ONLYSAVETIME=False
SEED=1988

NAME=$(BASENAME)_NMEAS_$(NMEAS)_ONLYSAVETIME_$(ONLYSAVETIME)
WDPATH=/home/bfmaier/SSA_symbiosis_fluctuating_fitness/$(NAME)
LOCALDIR=results_$(NAME)

USERATSERVER=bfmaier@groot0.biologie.hu-berlin.de
PYTHONPATH=/usr/local/bin/python2.7
MEMORY=2G

PARAMLISTSTRING="\[alpha\,\ measurements\]"
INTERNALLISTSTRING="\[Nmax\[\:2\]\]"
STANDARDLISTSTRING="\[corr_matrices\[0\],\ y0\[4\]\]"
GITREPOS="/home/bfmaier/tau-leaping-for-evolution"


#============================== FILENAMES ==============================

cfg:
	sed "s#NMEASUREMENTS#$(NMEASUREMENTS)#g" < config_dummy.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#MEMORY#$(MEMORY)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#NAME#$(BASENAME)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#SEED#$(SEED)#g" < config_file.py > __dummy__
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
	make wrap_every
	make gitupdateserver
	ssh $(USERATSERVER) "mkdir -p $(FOLDER); mkdir -p $(FOLDER)/custom_results"
	scp -r \
			simulation.py\
			wrap_results.py\
			config_file.py\
			job.py \
			submit_job.py\
			prepare_param_strings.py \
		$(USERATSERVER):$(FOLDER)
	ssh $(USERATSERVER) "cd $(FOLDER); $(PYTHONPATH) submit_job.py"

get_results:
	make wrap_results
	scp custom_wrap_results.py $(USERATSERVER):$(FOLDER)
	ssh $(USERATSERVER) "mkdir -p $(FOLDER)/custom_results/; cd $(FOLDER); $(PYTHONPATH) custom_wrap_results.py"
	mkdir -p $(LOCALDIR)/custom_results/
	cp custom_wrap_results.py 
	scp $(USERATSERVER):$(FOLDER)/custom_results/* $(LOCALDIR)/custom_results/

wrap_results:
	ssh $(USERATSERVER) "cd $(FOLDER); $(PYTHONPATH) wrap_results.py"

get_all_results:
	make wrap_results
	scp $(USERATSERVER):$(FOLDER)/*.p $(LOCALDIR)

wrap_every:
	mkdir -p $(LOCALDIR)
	cp \
			simulation.py\
			config_file.py\
			wrap_results.py \
			custom_wrap_results.py\
			prepare_param_strings.py \
	 $(LOCALDIR)/

clean:
	rm -rf *# *~ ./jobscripts/*
