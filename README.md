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
   
   This file holds the function `simulation_code` that will get called to start a single simulation with a fixed combination of parameters and a seed. All of those are passed in a dictionary called ``kwargs``. Ideally, the keys of ``kwargs`` are names of the parameters needed to initialize the simulation. In our case, ``simulation_code`` would load the class ``BrownianMotion`` from module ``brownian_motion``, feed the parameters to it, run the simulation and retrieve the result. The parameters are passed in a ``kwargs`` dictionary and subsequently can be used to do whatever we want to do with it. In the end, our simulation has a result, e.g. the trajectories *x*(t) of the particles. This result can be wrapped in whatever container we prefer and returned. QSuite will store it in a ``pickle`` and wrap it up once all jobs on the cluster are computed.
   
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

   Whithin fhis file we will edit the configuration of our experiment and add information about our queueing system. First, we have to decide which parameters should be used as *external* parameters. Those are parameters which are scanned using the cluster meaning that for every combination of those parameters one job is created on the cluster. Second, we decide for *internal* parameters, which means that inside of each job, every combination of those parameters will be simulated. Finally, we may decide that we don't need to scan all parameters, but just set *Δt*=0.01, so this will be a standard parameter (i.e. constant).
   
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
                           ( 'dt', dts[0] ),
                           ( 'x0', x0s[1] ),
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

