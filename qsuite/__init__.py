import os

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
import queuesys
