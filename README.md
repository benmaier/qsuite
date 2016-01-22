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

`qsuite_config.py`

   Whithin fhis file we will edit the configuration of our experiment and add information about our queueing system. I will address the structure of this file below. First, we have to decide which parameters should be used as *external* parameters. Those are parameters 



