from pyscenario import *
from util.arg import *


class Scenario(PyScenario):
    def get_description(self):
        return 'Empty Scenario'
        
    def get_map(self):
        return arg_get('-map', 'four-square')
