from pyscenario import *
from util.arg import *
from util.scene import RoadSideGen

class Scenario(PyScenario):
    def get_description(self):
        return 'Test random polygon at the border of roads'

    def get_map(self):
        return arg_get('-map', 'shapes-1')

    def init(self):
        gen = RoadSideGen(self.get_all_road_curves(), self.coord)
        self.dbg_draw_lines, self.dbg_draw_points = gen.gen_polys_dbg_draw_lines_and_points()

    def step(self, frame, t, dt):
        self.dbg_draw.add_point_group(self.dbg_draw_points, [1,1,1])
        self.dbg_draw.add_line_group(self.dbg_draw_lines, [1,1,1])
