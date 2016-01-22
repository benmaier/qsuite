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

### Without root access

```
$ sudo python setup.py install --user
```

Afterwards, add

```
export PATH=~/.local/bin:$PATH
```

to the file `~/.bash_profile` and do `$ source ~/.bash_profile`

## Philosophy

Oftentimes different array jobs on clusters have the same framework. You have to do a simulation of a certain kind which depends on a lot of parameters. Some of those parameters change the computation time, while others do not affect the computation's duration at all. Sometimes you have to run a simulation multiple times with the same parameters but different seeds in order to get satisfying statistics. However, you don't want to write a new bashscript everytime you change your mind about the combination of parameters for your batch script. The ROCS Queueing Suite gives a simple framework to generalize this work process while minimizing the researcher's work load. 

## Files

### ``simulation.py``

This file holds the function that will get called to start a single simulation with a fixed combination of parameters and a seed. So, this is where your research happens. If you want, you can write all your project's code in this single file. However, I recommend setting up a different repository containing your simulation code and updating it on the server every time you start an array job. The parameters are passed to the function ``simulation_code`` in a ``kwargs`` dictionary and can then get used to do whatever you want to do with it. In the end, every simulation has a result. This result can be wrapped in whatever container you prefer and returned. The computation suite will store it in a ``pickle`` and wrap it up once all jobs are computed.

### ``config_dummy.py``
