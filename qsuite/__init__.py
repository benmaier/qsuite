import os

customdir = os.path.join(os.path.expanduser("~"),".qsuite")

def rm(path):
    if os.path.exists(path):
        os.remove(path)

from .qconfig import *
from .template import *
from .qsuiteparse import *

