import numpy as np


class CurveBase:
    class ChangeLangeSolution:
        def __init__(self, status, curve=None, join_t=None):
            self.status = status
            self.curve = curve
            self.join_t = join_t
            
    def __init__(self, id, rgb):
        self.id = id
        self.rgb = rgb
        self.outgoing_curves = []
        self.incoming_curves = []
        self.outgoing_lane_curves = []
        self.incoming_lane_curves = []

    def get_outgoing_curves(self):
        return self.outgoing_curves

    def add_outgoing_curve(self, target):
        self.outgoing_curves.append(target)

    def add_incoming_curve(self, source):
        self.incoming_curves.append(source)
        
    def get_outgoing_lane_curves(self):
        return self.outgoing_lane_curves
        
    def get_incoming_lane_curves(self):
        return self.incoming_lane_curves

    def get_neighbor_lane_curves(self):
        return self.get_outgoing_lane_curves() + self.get_incoming_lane_curves()

    def add_outgoing_lane_curve(self, target):
        self.outgoing_lane_curves.append(target)

    def add_incoming_lane_curve(self, source):
        self.incoming_lane_curves.append(source)
        
    def t_to_normal(self, t):
        tang = self.t_to_tangent(t)
        return [-tang[1], tang[0]]

    def t_to_yaw(self, t):
        tang = self.t_to_tangent(t)
        return np.arctan2(tang[1], tang[0])

    def length_to_dt(self, t, length):
        return length / self.get_length()

    def dt_to_length(self, t, dt):
        return self.get_length() * dt

    def solve_lane_change_curve(self, src_pt, speed, lane_change_duration):
        return None
        
    def sample_t(self, seg_length, t0=0.0, t1=1.0):
        t = t0
        ts = [t]
        while t < t1:
            avail_length = min(seg_length, self.dt_to_length(t, 1.0-t))
            t = min(t+self.length_to_dt(t, avail_length), t1)
            ts.append(t)
        return ts
        
    def sample_pts(self, seg_length, t0=0.0, t1=1.0):
        return [self.t_to_point(t) for t in self.sample_t(seg_length, t0, t1)]
    