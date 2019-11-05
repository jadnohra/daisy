from pyscenario import *
from util.arg import *


class Scenario(PyScenario):
    def get_description(self):
        return 'A single car driving around'
        
    def get_map(self):
        return arg_get('-map', 'simple-straight')

    def init(self):
        self.car_1 = self.build_car().set_acceleration(40) \
                                .set_speed(g_param.sample_f('ego.speed', [20,80], 40)) \
                                .add_controller_wander() \
                                .place(self.get_first_road_curve_id(), 0.0)
