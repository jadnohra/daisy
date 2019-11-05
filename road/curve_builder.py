import numpy as np
from util.color import color_to_rgb


class CurveBuilder:
    def set_id(self, id):
        self._id = id
        return self

    def color(self, rgb_or_name):
        self._rgb = color_name_to_rgb[rgb_or_name]
        return self

    def length(self, length):
        self._length = length
        return self

    def angle(self, angle):
        self._angle = np.deg2rad(angle)
        if not self.has('shape'):
            self.shape('straight')
        return self

    def tangent_at_start(self, tang):
        self._tangent_at_start = tang
        return self

    def tangent_at_end(self, tang):
        self._tangent_at_end = tang
        return self

    def shape(self, shape):
        self._shape = shape
        return self

    def start_at(self, pos):
        self._start_at_pos = pos
        return self

    def start_at_t_of(self, id, t):
        self._start_at_rel = id
        self._start_at_t = t
        return self

    def start_at_start_of(self, id):
        self.start_at_t_of(id, 0)
        return self

    def start_at_end_of(self, id):
        self.start_at_t_of(id, 1)
        return self

    def end_at(self, pos):
        self._end_at_pos = pos
        return self

    def end_at_t_of(self, id, t):
        self._end_at_rel = id
        self._end_at_t = t
        return self

    def end_at_start_of(self, id):
        self.end_at_t_of(id, 0)
        return self

    def end_at_end_of(self, id):
        self.end_at_t_of(id, 1)
        return self

    def _attrname(self, key):
        return '_' + key

    def has(self, key):
        return hasattr(self, self._attrname(key))

    def get(self, key, dflt=None):
        name = self._attrname(key)
        return getattr(self, name) if hasattr(self, name) else dflt

    def set(self, key, value):
        name = self._attrname(key)
        setattr(self, name, value)