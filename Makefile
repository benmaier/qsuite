#============================== DEFINITIONS ============================
SHELL=/bin/bash

BASENAME=projecttitle
NMEASUREMENTS=10
PRIORITY=1
ONLYSAVETIME=False
SEED=1337

NAME=$(BASENAME)_NMEAS_$(NMEASUREMENTS)_ONLYSAVETIME_$(ONLYSAVETIME)
WDPATH=/path/at/server/$(NAME)
LOCALDIR=results_$(NAME)

USERATSERVER=username@server.com
PYTHONPATH=/serverpath/to/usr/bin/python
MEMORY=1G

#in the following, empty would be ok too, which would be represented as \[\]
#the parameters should be defined in "config_dummy.py"
PARAMLISTSTRING=\[params0\[2\:4\],\ params1\[\:-1\],\ measurements\]
INTERNALLISTSTRING=\[params2,\ params3\[4:0:-1\]\]
STANDARDLISTSTRING=\[params4\[0\],\ params5\[2\]\]
GITREPOS=/path/to/repo1 /path/to/repo2

QUEUESYS=PBS #or SGE


#============================== FILENAMES ==============================

cfg:
	sed "s#NMEASUREMENTS#$(NMEASUREMENTS)#g" < config_dummy.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#MEMORY#$(MEMORY)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#QUEUESYS#$(QUEUESYS)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#NAME#$(BASENAME)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#SEED#$(SEED)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#PYTHONPATH#$(PYTHONPATH)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#PARAMLISTSTRING#$(PARAMLISTSTRING)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#INTERNALLISTSTRING#$(INTERNALLISTSTRING)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#STANDARDLISTSTRING#$(STANDARDLISTSTRING)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#ONLYSAVETIME#$(ONLYSAVETIME)#g" < config_file.py > __dummy__
	mv __dummy__ config_file.py
	sed "s#WDPATH#$(WDPATH)#g" < config_file.py > __dummy__
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
	ssh $(USERATSERVER) "\
			mkdir -p $(WDPATH);\
			mkdir -p $(WDPATH)/custom_results;\
			mkdir -p $(WDPATH)/results;\
			mkdir -p $(WDPATH)/output;\
			"
	scp -r \
			simulation.py\
			wrap_results.py\
			config_file.py\
			job.py \
			submit_job.py\
			prepare_param_strings.py \
		$(USERATSERVER):$(WDPATH)
	ssh $(USERATSERVER) "cd $(WDPATH); $(PYTHONPATH) submit_job.py"

get_results:
	#make wrap_results
	scp custom_wrap_results.py $(USERATSERVER):$(WDPATH)
	ssh $(USERATSERVER) "mkdir -p $(WDPATH)/custom_results/; cd $(WDPATH); $(PYTHONPATH) custom_wrap_results.py"
	mkdir -p $(LOCALDIR)/custom_results/
	cp custom_wrap_results.py $(LOCALDIR) 
	scp $(USERATSERVER):$(WDPATH)/custom_results/* $(LOCALDIR)/custom_results/

wrap_results:
	ssh $(USERATSERVER) "cd $(WDPATH); $(PYTHONPATH) wrap_results.py"

get_all_results:
	make wrap_results
	scp $(USERATSERVER):$(WDPATH)/*.p $(LOCALDIR)

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
