import copy
import numpy as np


class RoadTrajectory:
    
    class CurveLocation:
        def __init__(self, curve=None, t=None):
            self.curve = curve
            self.t = t
            
    class CurveMarker:
        def __init__(self, parent):
            self.parent = parent
            self.curve_index = 0
            self.curve_location = None
            self.actual_road_pos = None
            self.error = None
            
        def get_location(self):
            return self.curve_location
        
        def _init(self, t0):
            if len(self.parent.curve_sequence) == 0:
                return
            self.curve_index = 0
            curve = self.parent.curve_sequence[0]
            self.curve_location = RoadTrajectory.CurveLocation(curve, t0)
            self.actual_road_pos = curve.t_to_point(t0)
            self.error = 0
        
        def _sync(self, road_pt):
            if len(self.parent.curve_sequence) == 0:
                return
            min_dist_sq = None
            min_t = None
            min_i = -1
            for i,curve in enumerate(self.parent.curve_sequence):
                t = curve.closest_t(road_pt)
                pt = curve.t_to_point(t)
                vec = np.subtract(pt, road_pt)
                dist_sq = np.dot(vec, vec)
                if min_i == -1 or dist_sq <= min_dist_sq:
                    min_dist_sq = dist_sq
                    min_i = i
                    min_t = t
            self.curve_index = min_i
            self.curve_location = RoadTrajectory.CurveLocation(
                                            self.parent.curve_sequence[min_i],
                                            min_t)
            self.actual_road_pos = road_pt
            self.error = np.sqrt(min_dist_sq)

        def _move(self, length):
            rest_length = length
            while rest_length > 0.0:
                curr_loc = self.get_location()
                dt = curr_loc.curve.length_to_dt(curr_loc.t, rest_length)
                new_t = curr_loc.t + dt
                if new_t >= 1.0:
                    clipped_dt = 1.0 - curr_loc.t
                    rest_length = rest_length - curr_loc.curve.dt_to_length(curr_loc.t, clipped_dt)
                    if self.curve_index + 1 < len(self.parent.curve_sequence):
                        self.curve_index = self.curve_index + 1
                        self.curve_location.curve = self.parent.curve_sequence[self.curve_index]
                        self.curve_location.t = 0.0
                    else:
                        self.curve_index = len(self.parent.curve_sequence)-1
                        self.curve_location.curve = self.parent.curve_sequence[self.curve_index]
                        self.curve_location.t = 1.0
                        rest_length = 0.0
                else:
                    self.curve_location.t = new_t
                    rest_length = 0.0
                
                
    
    def __init__(self, curve_sequence=[], t0=0):
        self.curve_sequence = curve_sequence
        self.marker = None
        if len(curve_sequence):
            self.marker = self.CurveMarker(self)
            self.marker._sync(self.curve_sequence[0].t_to_point(self.t0))
        
    def get_marker():
        return self.marker
        
    def get_curve_sequence(self):
        return self.curve_sequence
        
    def move_marker(self, length):
        if self.marker is not None:
            self.marker._move(length)