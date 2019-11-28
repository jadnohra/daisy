import numpy as np
from .curve import CurveBase


class SequenceCurve(CurveBase):
    def __init__(self, curve_sequence, id=None, rgb=[1.0,1.0,1.0]):
        super().__init__(id, rgb)
        self.curve_sequence = curve_sequence
        self.length = sum([x.get_length() for x in curve_sequence])

    def is_curved(self):
        return True

    def _normalize_t(self, index, frag_t):
        n = len(self.curve_sequence)
        return float(index+frag_t)/n

    def _denormalize_t(self, t):
        n = len(self.curve_sequence)
        index = np.clip(int(np.floor(t*n)), 0, n-1)
        return index, t*n-index

    def get_curve_sequence(self):
        return self.curve_sequence

    def closest_t(self, pt_world):
        def dist_sq(index, t):
            curve = self.curve_sequence[index]
            vec = np.subtract(curve.t_to_point(t), pt_world)
            return np.dot(vec, vec)
        closest_ts = [x.closest_t(pt_world) for x in self.curve_sequence]
        closest_distsqs = [dist_sq(i, closest_ts[i]) for i in range(len(closest_ts))]
        index = np.argmin(closest_distsqs)
        return self._normalize_t(index, closest_ts[index])

    def t_to_point(self, t):
        index, frag_t = self._denormalize_t(t)
        return self.curve_sequence[index].t_to_point(frag_t)

    def t_to_tangent(self, t):
        index, frag_t = self._denormalize_t(t)
        return self.curve_sequence[index].t_to_tangent(frag_t)

    def get_length(self):
        return self.length

    def length_to_dt(self, t, length):
        rest_length = length
        end_index, end_t = self._denormalize_t(t)
        while rest_length > 0.0 and end_index < len(self.curve_sequence):
            frag_max_length = self.curve_sequence[end_index].dt_to_length(end_t, 1.0-end_t)
            if frag_max_length >= rest_length:
                end_t = end_t + self.curve_sequence[end_index].length_to_dt(end_t, rest_length)
                break
            else:
                end_index = end_index + 1
                end_t = 0.0
                rest_length = rest_length - frag_max_length
        return self._normalize_t(end_index, end_t) - t

    def dt_to_length(self, t, dt):
        curr_index, curr_t = self._denormalize_t(min(t, t+dt))
        end_index, end_t = self._denormalize_t(max(t, t+dt))
        total_length = 0.0
        while curr_index < end_index:
            total_length = total_length + self.curve_sequence[curr_index].dt_to_length(curr_t, 1.0-curr_t)
            curr_index = curr_index + 1
            curr_t = 0.0
        total_length = total_length + self.curve_sequence[end_index].dt_to_length(curr_t, end_t-curr_t)
        return total_length

    def build_neighbor_curve(self, lane_index=0):
        pass

    def solve_lane_change_curve(self, src_pt, speed, lane_change_duration):
        return None