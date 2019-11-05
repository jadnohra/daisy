import numpy as np
from .curve import CurveBase
from util.math import intersect_two_lines


class StraightCurve(CurveBase):
    def __init__(self, id, rgb, world_start, world_end):
        super().__init__(id, rgb)
        self.world_start = world_start
        self.world_end = world_end
        len_vec = np.subtract(self.world_end, self.world_start)
        self.length = np.linalg.norm(len_vec)
        self.dir_vec = np.multiply(len_vec, 1.0/self.length)

    def is_curved(self):
        return False

    def closest_t(self, pt_world):
        vec = np.multiply(self.dir_vec, self.length)
        t = (np.dot(vec, np.subtract(pt_world, self.world_start))
                / np.dot(vec, vec))
        return np.clip(t, 0.0, 1.0)

    def t_to_point(self, t):
        return np.add(
                      np.multiply(self.world_start, 1.0-t),
                      np.multiply(self.world_end, t))

    def t_to_tangent(self, t):
        return self.dir_vec

    def get_length(self):
        return self.length
        
    def solve_lane_change_curve(self, src_pt, speed, lane_change_duration):
        l = speed * lane_change_duration
        r = np.subtract(self.world_start, src_pt)
        d = np.subtract(self.world_end, self.world_start)
        quadratic_coeffs = [np.dot(d, d), 2.0*np.dot(r, d), np.dot(r, r) - l*l]
        roots = np.roots(quadratic_coeffs)
        roots = [x for x in roots if np.isreal(x)]
        roots = [x for x in roots if x >= 0.0]
        if len(roots):
            t = np.amax(roots)
            if t <= 1.0:
                end_pt = self.t_to_point(t)
                return self.ChangeLangeSolution('done', StraightCurve(None, self.rgb, src_pt, end_pt), t)
            else:
                unclipped_end_pt = np.add(self.world_start, np.multiply(d, t))
                normal_line = [self.world_end, self.t_to_normal(1.0)]
                t = intersect_two_lines(normal_line, 
                                         [src_pt, np.subtract(unclipped_end_pt, src_pt)])[0]
                end_pt = np.add(normal_line[0], np.multiply(normal_line[1], t))
                if np.linalg.norm(np.subtract(end_pt, src_pt)) == 0:
                    return self.ChangeLangeSolution('chain')
                return self.ChangeLangeSolution('chain', StraightCurve(None, self.rgb, src_pt, end_pt))
        else:
            self.ChangeLangeSolution('unreachable')
        