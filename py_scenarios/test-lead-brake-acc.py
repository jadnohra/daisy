from pyscenario import *

class Scenario(PyScenario):
    def get_description(self):
        return 'Force a leading car to break, with parametric deceleration and ACC'

    def get_map(self):
        return 'simple-straight'

    def init(self):
        # Init main car
        self.car_1 = self.build_car().set_acceleration(40) \
                                .set_initial_speed(160).set_speed(160) \
                                .add_controller_wander() \
                                .place('A', 0.0)

        # Init lead car
        self.car_2 = self.build_car().set_acceleration(g_param.sample_f('braking_accel', [50,300], 100)) \
                                .set_initial_speed(160).set_speed(160) \
                                .add_controller_wander() \
                                .place('A', 0.1)

        # State machine
        self.triggered = False

    def step(self, frame, t, dt):
        if self.triggered == False:
            if t > 0.5:
                self.car_2.dynamics.set_speed(0)
                self.triggered = True
