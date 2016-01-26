# QSuite 

Provides a general framework to submit array jobs on an SGE (Sun Grid Engine) or a PBS (Portable Batch System) queueing system with multiple parameters and multiple measurements. Includes easy collection, possible costumized preprocessing and download of the jobs' results.

## Install

### Linux

```
$ sudo python setup.py install
```

### Mac OSX
First, do 

```
$ sudo python setup.py install
```

If you're not running a virtualenv python, make sure you add

```
export PATH=/opt/local/Library/Frameworks/Python.framework/Versions/Current/bin:$PATH
```

to the file `~/.bash_profile` and do `$ source ~/.bash_profile`

### Without Root Access

```
$ python setup.py install --user
```

Afterwards, add

```
export PATH=~/.local/bin:$PATH
```

to the file `~/.bash_profile` and do `$ source ~/.bash_profile`

### Windows

The code is written for cross platform usage, so theoretically it should work on Windows, too. However, nothing has been tested on Windows yet.

## Philosophy

Oftentimes different array jobs on clusters have the same framework. You have to do a simulation of a certain kind which depends on a lot of parameters. Some of those parameters change the computation time, while others do not affect the computation's duration at all. Sometimes you have to run a simulation multiple times with the same parameters but different seeds in order to get satisfying statistics. However, you don't want to write a new bashscript everytime you change your mind about the combination of parameters for your batch script. QSuite is a simple command line tool to generalize this work process while minimizing the researcher's work load. 

## How To

### Prelude

Say we want to simulate a Brownian motion of *N* particles in a one-dimensional box, interacting with a certain potential characterized by an interaction strength *V* and an interaction radius *r*. There are a bunch of parameters to consider:

* the number of particles *N*
* the length of the box *L*
* the temperature *T* of the system
* the interaction strength *V*
* the interaction radius *r*
* the maximal runtime *t*
* the time spacing *Δt*
* the initial conditons *x*(0)

Let's assume we don't know that some of the parameters can be rescaled and want to scan the whole parameter space. Luckily, a lot of the work for the project has already been done (yay!); at some point we wrote a python module ``brownian_motion`` which takes care of the simulation once it got the parameters passed. Consider it to look something like this

```python
class BrownianMotion:
    def __init__(N, L, T, V, r, tmax, dt, x0, seed=-1):
        ...

    def simulate():
        ...

    def get_trajectories():
        ...
```

### Initializing QSuite

So, now it's time to start the project. Do the following.

```
$ mkdir brownian; cd brownian
$ qsuite init
```

Three files appeared in your directory.

* `simulation.py`
   
   This file holds the function `simulation_code` that will get called to start a single simulation with a fixed combination of parameters and a seed. All of those are passed in a dictionary called ``kwargs``. Ideally, the keys of ``kwargs`` are names of the parameters needed to initialize the simulation. In our case, ``simulation_code`` would load the class ``BrownianMotion`` from module ``brownian_motion``, feed the parameters to it, run the simulation and retrieve the result. The parameters are passed in a ``kwargs`` dictionary and subsequently can be used to do whatever we want to do with it. In the end, our simulation has a result, e.g. the trajectories *x*(*t*) of the particles. This result can be wrapped in whatever container we prefer and returned. QSuite will store it in a ``pickle`` and wrap it up once all jobs on the cluster are computed.
   
   Our file will look like this
   ```python
   from brownian_motion import BrownianMotion()

   def simulation_code(kwargs):

       bm = BrownianMotion(**kwargs)
       bm.simulate()
       result = bm.get_trajectories()

       return result
   ```

* `qsuite_config.py`

   Within fhis file we will edit the configuration of our experiment and add information about our queueing system. First, we have to decide which parameters should be used as *external* parameters. Those are parameters which are scanned using the cluster meaning that for every combination of those parameters one job is created on the cluster. Second, we decide for *internal* parameters, which means that inside of each job, every combination of those parameters will be simulated. Finally, we may decide that we don't need to scan all parameters, but just set *Δt*=0.01, so this will be a standard parameter (i.e. constant).
   
   Our file will look like this
   ```python
   import os 

   #=========== SIMULATION DETAILS ========
   projectname = "brownian_motion"
   seed = -1
   N_measurements = 10 #we want 10 measurements for each parameter combination

   measurements = range(N_measurements)
   Ns = [ 1,10,100 ]
   Ls = [ 0.5, 1.0, 2.0 ]
   Ts = [ 0.5, 1.0, 2.0 ]
   Vs = [ 0.5, 1.0, 2.0 ]
   rs = [ 0.1, 0.2, 0.3 ]
   runtimes = [ 10.0, 100.0, 1000.0 ]
   x0s = [ 0., 0.5, 1.0 ] #in units of L
   dts = [ 0.001, 0.01]

   #this will have BrownianMotions()'s function parameter names
   external_parameters = [
                           ( 'Ls', Ls   ),
                           ( 'rs', rs   ),
                           ( None   , measurements ),
                          ]
   internal_parameters = [
                           ('N', Ns),
                           ('V', Vs[1:]),
                           ('T', Ts),
                          ]
   standard_parameters = [
                           ( 'dt', dts[1] ),
                           ( 'x0', x0s[0] ),
                           ( 'maxt', runtimes[-1] ),
                          ]
    #if this is true, only the simulation time will be saved and wrapped
   only_save_times = False

   #============== QUEUE ==================
   queue = "SGE"
   memory = "1G"
   priority = 0

   #============ CLUSTER SETTINGS ============
   username = "user"
   server = "server"
   useratserver = username + u'@' + server

   shell = "/bin/bash"
   pythonpath = "/usr/bin/python"
   basename = "bm_const_dt"
   name = basename + "_NMEAS_" + str(N_measurements) + "_ONLYSAVETIME_" + str(only_save_times)
   serverpath = "/home/"+username +"/"+ projectname + "/" + name 
   resultpath = serverpath + "/results"

   #=======================================
   localpath = os.path.join(os.getcwd(),"results_"+name)

   #========================
   #since we need the updated source code of the brownian_motion module on the server,
   #we add the git repo to get updated and installed.
   git_repos = [
                   ( "/home/"+username+"/brownian-motion", "python setup.py install --user" )
                ]
   ```

* ``.qsuite``
   
   This is a local QSuite configuration file which keeps track of the files relevant to your project. Don't mess around with it! Or do, what do I care.

### Submitting the Job

```bash
$ qsuite submit
```

Alternatively `$ qsuite start`. This will create a local directory `results_${name}` where all your relevant files will be copied to. It then copies all relevant files to the queueing system and submits the job.  

## Basic Functions

### Wrap the results
Once the job is finished, do

```bash
$ qsuite wrap
```

The results are now stored in `${serverpath}/results/results.p and `${serverpath}/results/times.p` and can be downloaded via `$ qsuite get all`.

### Customized Wrapping

Often you don't want all of the results, but a prepared version so you don't have to download everything. To this end, there's a template file for customized wrapping. You can get this template by typing

```bash
$ qsuite init customwrap
```

This copies the template to your working directory and will scp it to the server directory when you submit the job. In cas you already have a customwrap-file, you can add it as

```bash
$ qsuite set customwrap <filename>
```

When the job is done and the results are wrapped with `$ qsuite wrap`, you can call

```bash
$ qsuite customwrap
$ qsuite get
```

and the customly wrapped results will be copied to your local results directory.

### Update git repositories on the server

In the configuration file you can add git repositories which should be updated on the server. Add them to the list `git_repos` as a tuple. The first entry of the tuple should be the absolute path to the repository on the server and the second entry should be code which has to be executed after pulling (e.g. `python setup.py install --user`). Optionally, you can add a third tuple entry with the remote address of the repository (in case the repository is not yet present on the server). 

So the section in the configuration file could look like:

```python
git_repos = [
              ( "/home/"+username+"/qsuite",
                "python setup.py install --user",
                "https://github.com/benmaier/qsuite.git"
              )
            ]
```

If everything's configured, you can do

```bash
$ qsuite gitupdate  #or shorter:
$ qsuite git
```

to update everything necessary on the server. You don't have to, because `$ qsuite submit` will do that anyway.


### Add other files that qsuite should copy to the server

(or remove, s.t. those won't be copied anymore).

```bash
$ qsuite add <filename(s)>
$ qsuite rm <filename(s)>
```

This does not remove the file from the local directory. It just won't be copied anymore.

### Add a shell script to be executed before submission

```bash
$ qsuite set exec <filename>
```

### Change the filenames of the configuration and simulation files to other files

```bash
$ qsuite set cfg <filename>
$ qsuite set sim <filename>
```

### Copy Files from the Server directory to your local directory

```bash
$ qsuite get <filename without path> #get file from server directory
$ qsuite get         #get customly wrapped files from server/result directory
$ qsuite get results #get customly wrapped files from server/result directory (yes, same as $ qsuite get)
$ qsuite get all     #get all wrapped files from server/result directory
```

### Copy Files to the server directory from your local

```bash
$ qsuite scp <filename without path>
```

Alternatively: `$ qsuite sftp <filename>` or `$ qsuite ftp <filename>` (internally, copying is done via the sftp protocol).

### Execute a Command on the Server

```bash
$ qsuite ssh "command series"
```

### Change the default files for configuration and simulation

This will copy the file to the `.qsuite` directory in the user's home directory.

```bash
$ qsuite set defaultcfg <filename>
$ qsuite set defaultsim <filename>
$ qsuite set defaultcustomwrap <filename>
```

You can reset this to the initial template files via

```bash
$ qsuite reset defaultcfg 
$ qsuite reset defaultsim 
$ qsuite reset defaultcustomwrap 
```


### Checking the job status

```bash
$ qsuite qstat      #shows all jobs of the user 
$ qsuite qstat all  #shows the whole queue
$ qsuite qstat job  #shows the status of the current job
```

Alternatives to `qstat` are `stat` and `status`.



