from pyscenario import *
import util.scenario


class Scenario(PyScenario):
    def get_description(self):
        return 'Test spatial FOV functionality'
        
    def get_map(self):
        return 'four-square'
        
    def init(self):
        self.car_1 = self.build_car().set_acceleration(40).set_speed(160) \
                                        .add_controller_wander() \
                                        .place('A', 0.2)
        
        util.scenario.add_random_cars(self, 10, component_names=['wa'])
            
    def step(self, frame, t, dt):
        radius = 100.0
        fov_deg = 30.0
        ents_radius = self.spatial_eng.get_entities_in_radius(self.car_1, radius, self.car_entities)
        ents_fov = self.spatial_eng.get_entities_in_fov(self.car_1, radius, np.deg2rad(fov_deg), self.car_entities)
        if len(ents_radius) + len(ents_fov):
            print(f'{frame}. {len(ents_radius)}, {len(ents_fov)}')
        for entry in ents_radius:
            print (f' {entry[0].id} within {entry[1]} m.')
        for entry in ents_fov:
            print (f' {entry[0].id} within {entry[1]} m. at {np.rad2deg(entry[2])} deg.')
        