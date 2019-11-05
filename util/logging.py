from logging import *
from .arg import arg_has

basicConfig(format='%(levelname)s:%(message)s', level=(CRITICAL if arg_has('-no_logging') else INFO))