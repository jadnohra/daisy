from pyscenario import *
from road.sequence_curve_builder import build_curve_by_length

class Scenario(PyScenario):
    def get_description(self):
        return 'Test curve builder by length'

    def get_map(self):
        return 'simple-straight-then-arc'

    def init(self):
        self.built_curve = build_curve_by_length(self.get_road_curve('A'), 0.5, 40)
        self.sampled_pts = [self.coord.road_2d_to_spatial_3d_pt(x) for x in self.built_curve.sample_pts(2.0)]

    def step(self, frame, t, dt):
        self.dbg_draw.add_trajectory(self.built_curve.get_curve_sequence())
        self.dbg_draw.add_point_group(self.sampled_pts, [1.0, 1.0, 0.0])

