from pyscenario import *

class Scenario(PyScenario):
    def get_description(self):
        return 'Place a car on a curved road and make it brake after 1.5 seconds'

    def get_map(self):
        return 'simple-arc'

    def init(self):
        self.car_1 = self.build_car().set_acceleration(40).set_speed(100) \
                            .add_controller_wander() \
                            .place('A', 0.2)

    def step(self, frame, t, dt):
        if t > 1.5:
            self.car_1.dynamics.set_acceleration(120)
            self.car_1.dynamics.set_speed(0)
