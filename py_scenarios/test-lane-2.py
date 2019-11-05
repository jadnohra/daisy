from pyscenario import *
from util.arg import *
import util.scenario
from road.road_builder import RoadBuilder


class Scenario(PyScenario):
    def get_description(self):
        return 'A car changing lanes, with a faster one one of the lanes'
        
    def get_map(self):
        return arg_get('-map', 'two-lane-triangle')

    def get_map_parameters(self):
        return {'o':arg_get('-map_o', 5.0), 's':arg_get('-map_s', 'straight')}

    def init(self):
        self.next_trigger_time = 1.0
        self.car_1 = self.build_car().set_acceleration(40) \
                                .set_speed(30) \
                                .add_controller_proximity_brake() \
                                .add_controller_wander() \
                                .place('A', 0.0)
                                
        util.scenario.add_random_cars(self, 1, component_names=['wa', 'pb'])

    def step(self, frame, t, dt):
        if t > self.next_trigger_time:
            self.next_trigger_time = self.next_trigger_time + 2.0
            loc = self.car_1.wa.command_change_lane()
