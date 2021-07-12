QSuite
======

Provides a general framework to submit array jobs on an SGE (Sun Grid
Engine) or a PBS (Portable Batch System) queueing system with multiple
parameters and multiple measurements. Includes easy collection, possible
costumized preprocessing and download of the jobs' results.

Install
-------

In order for ``qsuite`` to function properly, you have to implement an
automatic login to your compute cluster. Say your username there is
``quser`` and the cluster address is ``qclust``. On your local machine,
your username is ``localuser``.

The following is adapted from
`linuxproblem.org <http://www.linuxproblem.org/art_9.html>`__. The first
you have to do is to generate a pair of RSA authentication keys like
it's done in the following. Note that in the current version of qsuite
rsa files encrypted with a passphrase are not supported, so you
shouldn't add one when you're using the commands below.

.. code:: bash

   localuser$ ssh-keygen -t rsa
   Generating public/private rsa key pair.
   Enter file in which to save the key (/home/localuser/.ssh/id_rsa): 
   Created directory '/home/localuser/.ssh'.
   Enter passphrase (empty for no passphrase): 
   Enter same passphrase again: 
   Your identification has been saved in /home/localuser/.ssh/id_rsa.
   Your public key has been saved in /home/localuser/.ssh/id_rsa.pub.
   The key fingerprint is:
   ab:cd:1e:4e quser@qclust

Now create an ``.ssh`` directory on the remote machine

.. code:: bash

   localuser$ ssh quser@qclust mkdir -p "~/.ssh"

and append your public key from your lcoal machine to the authorized key
file on the cluster

.. code:: bash

   localuser$ cat ~/.ssh/id_rsa.pub | ssh quser@qclust "cat >> ~/.ssh/authorized_keys"

Note the following: "Both the host and the client should have the
following permissions and owners:

-  ``~/.ssh`` permissions should be 700 (``cd ~; chmod 700 .ssh``)
-  ``~/.ssh`` should be owned by your account
-  ``~/.ssh/authorized_keys`` permissions should be 600
   (``cd ~/.ssh; chmod 600 authorized_keys``)
-  ``~/.ssh/authorized_keys`` should be owned by your account"

as per
`digitalocean <https://www.digitalocean.com/docs/droplets/resources/troubleshooting-ssh/authentication/>`__.

Linux, Mac OSX
~~~~~~~~~~~~~~

.. code:: bash

   $ sudo python setup.py install  #or
   $ sudo python3 setup.py install

Additional Mac OSX
~~~~~~~~~~~~~~~~~~

If you're not running a virtualenv python, make sure you add

.. code:: bash

   export PATH=/opt/local/Library/Frameworks/Python.framework/Versions/Current/bin:$PATH
   export PATH=/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin:$PATH
   export PATH=/opt/local/Library/Frameworks/Python.framework/Versions/3.5/bin:$PATH
   export PATH=/Library/Frameworks/Python.framework/Versions/3.5/bin:$PATH
   export PATH=/Library/Frameworks/Python.framework/Versions/2.7/bin:$PATH

to the file ``~/.bash_profile`` and do ``$ source ~/.bash_profile``

Also, you may encounter a problem with the python package
``cryptography``. If this is the case, try to reinstall it using

.. code:: bash

   LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install cryptography

Without root access
~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ python setup.py install --user

Afterwards, add

.. code:: bash

   export PATH=~/.local/bin:$PATH

to the file ``~/.bash_profile`` and do ``$ source ~/.bash_profile``

Windows
~~~~~~~

The code is written for cross platform usage, so theoretically it should
work on Windows, too. However, nothing has been tested on Windows yet.

Philosophy
----------

Oftentimes different array jobs on clusters have the same framework. You
have to do a simulation of a certain kind which depends on a lot of
parameters. Some of those parameters change the computation time, while
others do not affect the computation's duration at all. Sometimes you
have to run a simulation multiple times with the same parameters but
different seeds in order to get satisfying statistics. However, you
don't want to write a new bashscript everytime you change your mind
about the combination of parameters for your batch script. QSuite is a
simple command line tool to generalize this work process while
minimizing the researcher's work load.

How to
------

Prelude
~~~~~~~

Say we want to simulate a Brownian motion of *N* particles in a
one-dimensional box, interacting with a certain potential characterized
by an interaction strength *V* and an interaction radius *r*. There are
a bunch of parameters to consider:

-  the number of particles *N*
-  the length of the box *L*
-  the temperature *T* of the system
-  the interaction strength *V*
-  the interaction radius *r*
-  the maximal runtime *t*
-  the time spacing *Δt*
-  the initial conditons *x*\ (0)

Let's assume we don't know that some of the parameters can be rescaled
and want to scan the whole parameter space. Luckily, a lot of the work
for the project has already been done (yay!); at some point we wrote a
python module ``brownian_motion`` which takes care of the simulation
once it got the parameters passed. Consider it to look something like
this

.. code:: python

   class BrownianMotion:
       def __init__(N, L, T, V, r, tmax, dt, x0, seed=-1):
           ...

       def simulate():
           ...

       def get_trajectories():
           ...

Initializing QSuite
~~~~~~~~~~~~~~~~~~~

So, now it's time to start the project. Do the following.

.. code:: bash

   $ mkdir brownian; cd brownian
   $ qsuite init

Three files appeared in your directory.

-  ``simulation.py``

   This file holds the function ``simulation_code`` that will get called
   to start a single simulation with a fixed combination of parameters
   and a seed. All of those are passed in a dictionary called
   ``kwargs``. Ideally, the keys of ``kwargs`` are names of the
   parameters needed to initialize the simulation. In our case,
   ``simulation_code`` would load the class ``BrownianMotion`` from
   module ``brownian_motion``, feed the parameters to it, run the
   simulation and retrieve the result. The parameters are passed in a
   ``kwargs`` dictionary and subsequently can be used to do whatever we
   want to do with it. In the end, our simulation has a result, e.g. the
   trajectories *x*\ (*t*) of the particles. This result can be wrapped
   in whatever container we prefer and returned. QSuite will store it in
   a ``pickle`` and wrap it up once all jobs on the cluster are
   computed.

   Our file will look like this

.. code:: python

   from brownian_motion import BrownianMotion

   def simulation_code(kwargs):

      bm = BrownianMotion(**kwargs)
      bm.simulate()
      result = bm.get_trajectories()

      return result

-  ``qsuite_config.py``

   Within fhis file we will edit the configuration of our experiment and
   add information about our queueing system. First, we have to decide
   which parameters should be used as *external* parameters. Those are
   parameters which are scanned using the cluster meaning that for every
   combination of those parameters one job is created on the cluster.
   Second, we decide for *internal* parameters, which means that inside
   of each job, every combination of those parameters will be simulated.
   Finally, we may decide that we don't need to scan all parameters, but
   just set *Δt*\ =0.01, so this will be a standard parameter (i.e.
   constant).

   Our file will look like this

.. code:: python

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
                          ( 'L', Ls   ),
                          ( 'r', rs   ),
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
                          ( 'tmax', runtimes[-1] ),
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
                  ( "/home/"+username+"/brownian-motion", pythonpath + " setup.py install --user" )
               ]

-  ``.qsuite``

   This is a local QSuite configuration file which keeps track of the
   files relevant to your project. Don't mess around with it! Or do,
   what do I care.

Submitting the job
~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ qsuite submit

Alternatively ``$ qsuite start``. This will create a local directory
``results_${name}`` where all your relevant files will be copied to. It
then copies all relevant files to the queueing system and submits the
job.

In case something went wrong in a job and it crashed or you deleted it,
you can resubmit that job using

.. code:: bash

   $ qsuite submit $ARRAY_ID

where ``$ARRAY_ID`` is the job number for which you want to restart the
calculation. Note that the job must have been submitted before. You can
also submit ranges of array IDs and multiple array IDs, e.g.

.. code:: bash

   $ qsuite submit 1 65 578-1000 3

Sometimes you want to resubmit all jobs which had an error or all jobs
which are still in "waiting..." mode (because there was an uncaught
error). You can do

.. code:: bash

   $ qsuite submit err        # submits all jobs which had a caught error
   $ qsuite submit wait       # submits all jobs which are in waiting status
   $ qsuite submit err wait   # submits all jobs which are in either of above

where ``$ARRAY_ID`` is the job number for which you want to restart the
calculation. Note that the job must have been submitted before.

Basic functions
---------------

Seed behavior
~~~~~~~~~~~~~

QSuite checks for the variable ``seed`` in the file
``qsuite_config.py``. If it is set, if it is not ``None`` and if it is
``>= 0``, each parameter configuration gets an own seed, which is
``seed + ip`` where ``ip`` is the integer id of the parameter
configuration. It will be passed as ``kwargs['seed']`` to the simulation
function. If ``seed``, however, is a keyword already set by the user,
the parameter seed will be passed as ``kwargs['randomseed']``.

Error handling
~~~~~~~~~~~~~~

Putting errors in code is each scientist's favorite hobby. Hence,
``qsuite`` catches occuring errors and writes them into progress files,
s.t. you can see the job is not running anymore by typing
``qsuite stat``. However, often you want to explicitly see the errors.
Hence, you can use

.. code:: bash

   $ qsuite err $ARRAY_ID

where ``$ARRAY_ID`` is the job number for which you want to see the
error (starts counting at 1). This is the number which is left from the
progress bar when you call ``qsuite stat``. If everything failed, you
can just do

.. code:: bash

   $ qsuite err

and ``qsuite`` automatically assumes that you mean the job with array ID
1.

Wrap the results
~~~~~~~~~~~~~~~~

Once the job is finished, do

.. code:: bash

   $ qsuite wrap

The results are now stored in ``${serverpath}/results/results.p.gz`` and
``${serverpath}/results/times.p`` and can be downloaded via
``$ qsuite get all``. Beware! The result file will be compressed with
the ``gzip`` format.

Copy files from the server directory to your local working directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ qsuite get <filename without path> #get file from server directory
   $ qsuite get         #get customly wrapped files from server/result directory
   $ qsuite get results #get customly wrapped files from server/result directory (yes, same as $ qsuite get)
   $ qsuite get all     #get all wrapped files from server/result directory

Beware! Pickled files will be compressed with the ``gzip`` module. Load
them with
``import pickle; import gzip; pickle.load(gzip.open('filename','rb'))``
or unzip them using ``gzip -d results.p.gz``

Preprocess data locally
~~~~~~~~~~~~~~~~~~~~~~~

Often enough ``results.p.gz`` contains a g-zipped array of floats which
you need as a numpy array or as mean and error. After downloading (and
without necessary unzipping), change to the result directory

.. code:: bash

   $ cd results_$NAME/      # contains result.p or results.p.gz
   $ qsuite convert numpy   # unzips results.p.gz, loads, converts to numpy array, saves as `./results.npy`
   $ qsuite convert meanerr # does everything as `convert numpy` does, then looks builds mean and error over all measurements. Saves as `./results.mean_err.npz`

You can load ``./results.mean_err.npz`` as

.. code:: python

   import numpy as np
   data = np.load('./results_mean_err.npz')
   mean = data['mean']
   err = data['err']

Customized wrapping
~~~~~~~~~~~~~~~~~~~

Often you don't want all of the results, but a prepared version so you
don't have to download everything. To this end, there's a template file
for customized wrapping. You can get this template by typing

.. code:: bash

   $ qsuite init customwrap

This copies the template to your working directory and will scp it to
the server directory when you submit the job. In case you already have a
customwrap-file, you can add it as

.. code:: bash

   $ qsuite set customwrap <filename>

When the job is done and the results are wrapped with ``$ qsuite wrap``,
you can call

.. code:: bash

   $ qsuite customwrap
   $ qsuite get

and the customly wrapped results will be copied to your local results
directory. Beware! The pickled result files will be compressed with the
``gzip`` module. Load them with
``import pickle; import gzip; pickle.load(gzip.open('filename','rb'))``.

Update git repositories on the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the configuration file you can add git repositories which should be
updated on the server. Add them to the list ``git_repos`` as a tuple.
The first entry of the tuple should be the absolute path to the
repository on the server and the second entry should be code which has
to be executed after pulling (e.g. ``python setup.py install --user``).
Optionally, you can add a third tuple entry with the remote address of
the repository (in case the repository is not yet present on the
server).

So the section in the configuration file could look like:

.. code:: python

   git_repos = [
                 ( "/home/"+username+"/qsuite",
                   "python setup.py install --user",
                   "https://github.com/benmaier/qsuite.git"
                 )
               ]

If everything's configured, you can do

.. code:: bash

   $ qsuite gitupdate  #or shorter:
   $ qsuite git

to update everything necessary on the server. You don't have to, because
``$ qsuite submit`` will do that anyway.

Add other files that qsuite should copy to the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(or remove, s.t. those won't be copied anymore).

.. code:: bash

   $ qsuite add <filename(s)>
   $ qsuite rm <filename(s)>

This does not remove the file from the local directory. It just won't be
copied anymore.

Add a shell script to be executed before submission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ qsuite set exec <filename>

Change the filenames of the configuration and simulation files to other files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ qsuite set cfg <filename>
   $ qsuite set sim <filename>

Copy files to the server directory from your local working directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ qsuite scp <filename without path>

Alternatively: ``$ qsuite sftp <filename>`` or
``$ qsuite ftp <filename>`` (internally, copying is done via the sftp
protocol).

Execute a command on the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Careful! It's not interactive yet, so you won't be able to enter
passwords or answer questions or anything of that matter.

.. code:: bash

   $ qsuite ssh "command series"

If you want to do something in the server directory of the project, you
can use the keyword ``DIR``, e.g.

.. code:: bash

   $ qsuite ssh "ls DIR/results/"

and qsuite will replace it with the right path given in
``qsuite_config.py``.

Change the default files for configuration and simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This will copy the file to the ``.qsuite`` directory in the user's home
directory.

.. code:: bash

   $ qsuite set defaultcfg <filename>
   $ qsuite set defaultsim <filename>
   $ qsuite set defaultcustomwrap <filename>

You can reset this to the initial template files via

.. code:: bash

   $ qsuite reset defaultcfg 
   $ qsuite reset defaultsim 
   $ qsuite reset defaultcustomwrap 

Checking the job status
~~~~~~~~~~~~~~~~~~~~~~~

The following gives you a fancy output with a progress bar and an
estimated time remaining.

.. code:: bash

   $ qsuite stat

Sometimes, it's helpful to see which parameters a certain job has in
order to figure out why it's running so slowly. Do

.. code:: bash

   $ qsuite stat p

The following gives you the standard queue output.

.. code:: bash

   $ qsuite qstat      #shows all jobs of the user 
   $ qsuite qstat all  #shows the whole queue
   $ qsuite qstat job  #shows the status of the current job

Alternatives to ``qstat`` are ``stat`` and ``status``.

Estimate the size of the produced data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ qsuite estimate $NUMBER_OF_BYTES_PER_PARAMETER_COMBINATION
   $ qsuite estimatespace $NUMBER_OF_BYTES_PER_PARAMETER_COMBINATION
   $ qsuite data $NUMBER_OF_BYTES_PER_PARAMETER_COMBINATION

Give an estimation of the size of the produced data. An example is the
following. Your function ``simulation_code`` returns a list of 2
``numpy``-arrays, each containing 100 ``numpy``-floats. Each of those
floats has a size of 8 bytes. Now you can estimate the size of the
produced data as

.. code:: bash

   $ qsuite estimate "2*100*8"

and qsuite automatically evaluates the multiplication.

Testing the simulation locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ qsuite test                    # tests job with external job id 0 and saves in ./.test
   $ qsuite test $EXTERNALJOBID     # tests job with given external job id and saves in ./.test
   $ qsuite test $EXTERNALJOBID <directory>    # tests job with given external job id and saves in <directory>

Computing everything locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In your ``qsuite_config.py`` add the line

.. code:: python

   n_local_cpus = X

where X is the number of free CPUs that you can use for local
computations. If this line is not given, ``qsuite`` assumes
``n_local_cpus = 1``.

Do

.. code:: bash

   $ qsuite local

The results will be subsequently wrapped locally and moved to the
simulation directory. However, if there occurs an error you can wrap
manually with

.. code:: bash

   $ qsuite wrap local

Changing the order of the result array
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, you wrote an anlysis script that expects the indices of the
result array/list to be ordered in a certain way. However, you might
have changed the order of the parameters in the ``qsuite_config``-file
for various reasons. Instead of changing the indexing in the analysis
file, you can simply load the results and define a new parameter order.
For instance, your config was set up as follows:

.. code:: python

   external_parameters = [
                           ( 'r0', r0s),
                           ( 'w0', w0s),
                           ( None   , measurements ),
                         ]
   internal_parameters = [
                           ('p5', p5s),
                         ]

However, in your analysis file you want to access the results as
``data[iw0,ir0,meas,ip5]``. What you can do is to set up the following
in your analysis file

.. code:: python

   import numpy as np
   from qsuite.tools import change_result_parameter_order, change_meanerr_parameter_order

   with open('results.npy','rb') as f:
       data = np.load(f)
       data_new = change_result_parameter_order(data,['w0','r0',None,'p5'])

   with open('results_mean_err.npz','rb') as f:
       data = np.load(f)
       mean = data['mean']
       mean_new = change_meanerr_parameter_order(mean,['w0','r0','p5'])

Then, the new arrays carry the data in the desired order. Also works on
the original pickled list.
