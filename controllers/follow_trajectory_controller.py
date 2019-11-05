

class FollowTrajectoryController:
    def __init__(self):
        self.bind(None)

    def bind(self, car):
        self.car = car

    def unbind(self, car):
        self.car = None

    def step(self, t, dt):
        move_length = self.car.dynamics.get_speed() * dt
        self.car.trajectory.move_marker(move_length)
        if self.car.trajectory.marker is not None:
            new_loc = self.car.trajectory.marker.get_location()
            self.car.location.set(new_loc.curve, new_loc.t)
