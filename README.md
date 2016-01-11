# ROCS Queueing Suite 

Provides a general framework to submit array jobs on an SGE (Sun Grid Engine) or a PBS (Portable Batch System) queueing system with multiple parameters and multiple measurements. Includes easy collection, possible costumized preprocessing and download of the jobs' results.

## Philosophy

Oftentimes different array jobs on clusters have the same framework. You have to do a computation of a certain kind which depends on a lot of parameters. Some of those parameters change the computation time, while others do not affect the computation's duration at all. Sometimes you have to run the computation multiple times with the same parameters but different seeds in order to get satisfying statistics. However, you don't want to write a new bashscript everytime you change your mind about the combination of parameters for your batch script. The ROCS Queueing Suite is gives a simple framework to generalize this work process minimizing time. 

In the ``Makefile``, 
