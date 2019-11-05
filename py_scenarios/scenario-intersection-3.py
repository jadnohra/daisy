from pyscenario import *

class Scenario(PyScenario):
    def get_description(self):
        return 'Force a car to enter an intersection aggressively, just when another car is about to reach it (using a dynamics solver)'

    def get_map(self):
        return 'simple-intersection'

    def init(self):
        # Init main car
        self.car_1 = self.build_car().set_acceleration(40).set_speed(140) \
                            .add_controller_wander() \
                            .place('A', 0.2)

        # Init crossing car
        self.car_2 = self.build_car().set_acceleration(120) \
                            .add_controller_wander() \
                            .set_color('red') \
                            .place('B', 0.7)
        self.car_2_target_speed = 160

        # State machine
        self.triggered = False

    def solver_should_start(self, dt):
        car_1_loc = self.car_1.location
        assert(car_1_loc.curve.id == 'A' and car_1_loc.t <= 1.0)
        eta_A = self.car_1.dynamics.solve_eta_on_curve(car_1_loc.curve, car_1_loc.t, 1.0)
        car_2_loc = self.car_2.location
        eta_B = self.car_2.dynamics.solve_eta_on_curve_ex(car_2_loc.curve, car_2_loc.t, 1.0,
            0.0, self.car_2_target_speed, self.car_2.dynamics.get_acceleration())
        return (eta_B >= eta_A - dt)

    def step(self, frame, t, dt):
        if self.triggered == False:
            if self.solver_should_start(dt):
                self.car_2.dynamics.set_speed(self.car_2_target_speed)
                self.triggered = True
