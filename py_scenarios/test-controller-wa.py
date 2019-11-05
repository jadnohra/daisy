from pyscenario import *
from util.arg import *


class Scenario(PyScenario):
    def get_description(self):
        return 'Test wander controller'
        
    def get_map(self):
        return arg_get('-map', 'four-square')

    def init(self):
        self.build_car().set_acceleration(40). \
                set_speed(80). \
                add_controller_wander(). \
                place(self.get_first_road_curve_id(), 0.0)
        
