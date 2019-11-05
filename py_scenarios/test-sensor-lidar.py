from pyscenario import *
from util.arg import *
import util.scenario
from util.scene import RoadSideGen

class Scenario(PyScenario):
    def get_description(self):
        return 'Test LiDAR sensor'
        
    def get_map(self):
        return g_param.sample('map', ['four-square', 'split-triangle'], 'four-square')
        
    def get_map_parameters(self):
        return {'l':arg_get('-map_l', 75.0)}
        
    def init(self):
        self.car_1 = self.build_car().set_acceleration(40) \
                                .set_speed(g_param.sample_f('ego.speed', [20,80], 40)) \
                                .add_controller_wander() \
                                .add_controller_proximity_brake() \
                                .add_sensor_lidar(g_param.sample_b('lidar.rotate', 'bool', False)) \
                                .place('A', 0.2)
            
        util.scenario.add_random_cars(self, g_param.sample_i('cars.count', [0, 30], 15), component_names=['wa', 'pb'])
        
        gen = RoadSideGen(self.get_all_road_curves(), self.coord)
        gen.place_scene_boxes(self)