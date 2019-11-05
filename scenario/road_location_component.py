

class RoadLocationComponent:
    def __init__(self):
        self.car = None
        self.curve = None
        self.t = None
        self.road_pos = None
        self.road_yaw = None

    def set(self, curve, t):
        self.set_full(curve, t, curve.t_to_point(t), curve.t_to_yaw(t))
    
    def set_full(self, curve, t, pos, yaw):
        self.curve = curve
        self.t = t
        self.pos = pos
        self.yaw = yaw
