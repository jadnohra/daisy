from pyscenario import *
from util.arg import *
import util.scenario
import numpy as np


class Scenario(PyScenario):
    def get_description(self):
        return 'Test spatial taycast functionality'
        
    def get_map(self):
        return 'four-square'
        
    def get_map_parameters(self):
        return {'l':arg_get('-map_l', 50.0)}    
        
    def init(self):
        util.scenario.add_random_cars(self, arg_get('-car_count', 5), component_names=['wa'])

    def step(self, frame, t, dt):
        origin = np.multiply(self.coord.height_3d(), 1.7)
        azimuth_center = (t * 20.0) - int((t*2.0)/360)*360
        hits = self.spatial_eng.cast_rays_spherical(origin, np.deg2rad(azimuth_center-90), np.deg2rad(azimuth_center+90), 60,
                                np.deg2rad(-20), np.deg2rad(-3), 40, 300.0)
        for hit in hits:
            self.dbg_draw.add_point(hit[1])
            