from pyscenario import *
import random

class Scenario(PyScenario):
    def get_description(self):
        return 'Test yaw functionality'

    def get_map(self):
        return 'simple-arc'

    def init(self):
        self.car_1 = self.build_car().set_acceleration(40).set_speed(20) \
                                        .add_controller_wander() \
                                        .place('A', 0.0)


    def step(self, frame, t, dt):
        print(f'{frame}. {np.rad2deg(self.car_1.spatial.yaw_road)}')