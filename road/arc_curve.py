import numpy as np
from .curve import CurveBase


class ArcCurve(CurveBase):
    def __init__(self, id, rgb, 
                 world_start, world_end,
                 world_arc_center, arc_rad,
                 arc_angle_start, arc_angle_end,
                 arc_path_delta):
        super().__init__(id, rgb)
        self.world_start = world_start
        self.world_end = world_end
        self.world_arc_center = world_arc_center
        self.arc_rad = arc_rad
        self.arc_angle_start = arc_angle_start
        self.arc_angle_end = arc_angle_end
        self.arc_path_delta = arc_path_delta
        self.length = np.abs(self.arc_rad * self.arc_path_delta)

    def is_curved(self):
        return True

    def closest_t(self, pt_world):
        shift_center = np.subtract(self.world_arc_center, pt_world)
        arc_delta = self.arc_path_delta
        theta = np.arctan2(-shift_center[1], -shift_center[0])
        theta = theta + 2*np.pi if theta < 0 else theta
        t = (theta - self.arc_angle_start) / arc_delta
        if t < 0.0 or t > 1.0:
            dist_start = np.linalg.norm(np.subtract(pt_world, self.world_start))
            dist_end = np.linalg.norm(np.subtract(pt_world, self.world_end))
            return 0.0 if dist_start < dist_end else 1.0
        else:
            return t

    def t_to_point(self, t):
        phi = self.arc_angle_start + self.arc_path_delta * t
        local_arc_pt = [x * self.arc_rad for x in
                        [np.cos(phi), np.sin(phi)]]
        return np.add(self.world_arc_center, local_arc_pt)

    def t_to_tangent(self, t):
        phi = self.arc_angle_start + self.arc_path_delta * t
        sgn = np.sign(self.arc_path_delta)
        return [-np.sin(phi) * sgn, np.cos(phi) * sgn]

    def get_length(self):
        return self.length