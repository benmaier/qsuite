import os

__version__ = "0.4.14"

__author__ = "Benjamin F. Maier"
__copyright__ = "Copyright 2015-2021, " + __author__
__credits__ = [__author__]
__license__ = "MIT"
__maintainer__ = __author__
__email__ = "contact@benmaier.org"
__status__ = "Development"

customdir = os.path.join(os.path.expanduser("~"),".qsuite")

def rm(path):
    if os.path.exists(path):
        os.remove(path)

def mkdirp(path):
    if not os.path.exists(path):
        os.mkdir(path)

from .qconfig import *
from .template import *
from .qsuiteparse import *
from .ssh import *
from .submitjob import *
from .printparams import *
import qsuite.queuesys as queuesys
