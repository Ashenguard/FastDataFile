# noinspection PyUnresolvedReferences
from ..FastDataFile import *


def _init():
    import sys
    import FastDataFile

    sys.modules['FDF'] = FastDataFile


_init()