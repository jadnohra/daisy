from pyscenario import *

class Scenario(PyScenario):
    def get_description(self):
        return 'Force a car to enter an intersection aggressively, just when another car is about to reach it'

    def get_map(self):
        return 'simple-intersection'

    def init(self):
        # Init main car
        self.car_1 = self.build_car().set_acceleration(40).set_speed(140) \
                            .add_controller_wander() \
                            .place('A', 0.2)

        # Init crossing car
        self.car_2 = self.build_car().set_dynamics('point-kinematic') \
                            .add_controller_wander() \
                            .set_color('red') \
                            .place('B', 0.7)

        # State machine
        self.triggered = False

    def step(self, frame, t, dt):
        if self.triggered == False:
            if self.car_1.location.t > 0.7:
                self.car_2.dynamics.set_speed(160)
                self.triggered = True