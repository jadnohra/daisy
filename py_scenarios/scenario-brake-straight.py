from pyscenario import *

class Scenario(PyScenario):
    def get_description(self):
        return 'Place a car and make it brake after 5 seconds'

    def get_map(self):
        return 'four-square'

    def init(self):
        self.car_1 = self.build_car().set_acceleration(40).set_speed(160) \
                            .add_controller_wander() \
                            .place('A', 0.2)

    def step(self, frame, t, dt):
        if t > 5.0:
            self.car_1.dynamics.set_acceleration(120)
            self.car_1.dynamics.set_speed(0)

