from enum import Enum
from .follow_trajectory_controller import FollowTrajectoryController
from .manoeuvre_controller import DevelopLaneChangeController


class ActController:
    class Mode(Enum):
        IDLE = 0
        FOLLOW_TRAJECTORY = 1
        CHANGE_LANE = 2
    
    def __init__(self):
        self.car = None
        self.mode = self.Mode.FOLLOW_TRAJECTORY
        self.controller = None

    def bind(self, car):
        self.car = car
        self._ensure_mode_controller(self.mode)

    def unbind(self, car):
        self.car = None

    def set_mode(self, mode):
        self._ensure_mode_controller(mode)
        
    def _ensure_mode_controller(self, mode):
        if mode != self.mode or self.controller is None:
            if self.controller is not None:
                self.controller.unbind(self.car)
                self.controller = None
            self.mode = mode
            if self.mode == self.Mode.FOLLOW_TRAJECTORY:
                self.controller = FollowTrajectoryController()
            elif self.mode == self.Mode.CHANGE_LANE:
                self.controller = DevelopLaneChangeController(self.car.trajectory)
            if self.controller is not None:
                self.controller.bind(self.car)

    def step(self, t, dt):
        if self.controller is not None:
            self.controller.step(t, dt)
        