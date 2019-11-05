import numpy as np
import copy

class DevelopLaneChangeController:
    def __init__(self, ref_trajectory):
        self.bind(None)
        self.ref_trajectory = copy.copy(ref_trajectory)

    def bind(self, car):
        self.car = car
        self.t0 = None

    def unbind(self, car):
        self.car = None

    def step(self, t, dt):
        if self.t0 is None:
            self.t0 = t
        move_length = self.car.dynamics.get_speed() * dt
        self.ref_trajectory.move_marker(move_length)
        if self.ref_trajectory.marker is not None:
            new_loc = self.ref_trajectory.marker.get_location()
            ref_road_pos = new_loc.curve.t_to_point(new_loc.t)
            road_pos = np.add(ref_road_pos, np.multiply(new_loc.curve.t_to_normal(new_loc.t), 2.0*(t-self.t0)))
            ref_road_yaw = new_loc.curve.t_to_yaw(new_loc.t) 
            road_yaw = ref_road_yaw # TODO also alternate yaw
            self.car.location.set_full(new_loc.curve, new_loc.t, road_pos, road_yaw)
