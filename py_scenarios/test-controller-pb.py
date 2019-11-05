from pyscenario import *
from util.arg import *
import util.scenario

class Scenario(PyScenario):
    def get_description(self):
        return 'Test proximity brake controller'
        
    def get_map(self):
        return arg_get('-map', 'four-square')
    
    def init(self):
        util.scenario.add_random_cars(self, arg_get('-car_count', 10), component_names=['wa', 'pb'])