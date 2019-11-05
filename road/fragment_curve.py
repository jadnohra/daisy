import numpy as np
from .curve import CurveBase

class FragmentCurve(CurveBase):
    def __init__(self, ref_curve, t0, t1):
        super().__init__(None, None)
        self.ref_curve = ref_curve
        self.t0 = t0
        self.t1 = t1
        self.length = self.ref_curve.dt_to_length(self.t0, self.t1-self.t0)
        
    def _t_to_ref_t(self, t):
        return self.t0 + (self.t1-self.t0) * t
        
    def _ref_t_to_t(self, t):
        return (t-self.t0) / (self.t1-self.t0)
        
    def is_curved(self):
        return self.ref_curve.is_curved()

    def closest_t(self, pt_world):
        ref_t = self.ref_curve.closest_t(pt_world)
        return np.clip(self._ref_t_to_t(ref_t), 0.0, 1.0)

    def t_to_point(self, t):
        return self.ref_curve.t_to_point(self._t_to_ref_t(t))

    def t_to_tangent(self, t):
        return self.ref_curve.t_to_tangent(self._t_to_ref_t(t))

    def get_length(self):
        return self.length