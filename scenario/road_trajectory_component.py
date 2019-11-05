import copy
import numpy as np
from road.road_trajectory import RoadTrajectory

class RoadTrajectoryComponent(RoadTrajectory):

    def __init__(self):
        super().__init__()
        self.reset_curve_sequence([])
    
    def bind(self, car):
        self.car = car

    def unbind(self, car):
        self.car = None
    
    def reset_curve_sequence(self, curve_sequence):
        self.curve_sequence = copy.copy(curve_sequence)
        self.marker = None
        
    def update_curve_sequence(self, curve_sequence):
        self.curve_sequence = copy.copy(curve_sequence)
        if self.marker is not None:
            self.marker.curve_index = None
            for i,curve in enumerate(self.curve_sequence):
                if self.marker.curve_location.curve == curve:
                    self.marker.curve_index = i
            if self.marker.curve_index is None:
                self.marker = None
    
    def update_marker(self): #TODO call as update function after physics step?
        if self.marker is None:
            if (self.curve_sequence is not None 
                and len(self.curve_sequence) > 0
                and self.car.location.curve is not None):
                self.marker = self.CurveMarker(self)
                self.marker._sync(self.car.location.pos)
        else:
            pass #TODO, check if desync happened?
        
    def move_marker(self, length):
        self.update_marker()
        if self.marker is not None:
            self.marker._move(length)