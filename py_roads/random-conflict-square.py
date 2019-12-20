from pyroad import *
from road.road_builder import RoadBuilder
import numpy as np
import collections
import random


class Road(PyRoad):
    def get_description(self):
        return 'A square region with random intersecting trajectories'

    def get_asciiart(self):
        return \
'''
             |----A----|
             |..       |
             D  ..*..  B
             |       ..|
             |----C----|
'''

    def get_param_descriptions(self):
        return {'l':'Main length of square (default: 75)',
                'n':'Number of random trajectories (default:4)',
                'cd':'Clearance distance between starting points (default:4)',
                }

    # Build a basic triangle with no arcs
    @staticmethod
    def build_ref_road(l):
        b = RoadBuilder()
        b.curve('A').start_at([0,0]).length(l).angle(0)
        b.curve('B').start_at_end_of('A').length(l).angle(90)
        b.link('A', 'B')
        b.curve('C').start_at_end_of('B').length(l).angle(180)
        b.link('B', 'C')
        b.curve('D').start_at_end_of('C').length(l).angle(-90)
        b.link('C', 'D').link('D', 'A')
        return b.build()

    Point = collections.namedtuple('Point', 'road t x y')

    @staticmethod
    def is_dist_away(pt, conflict_segs, road, min_dist):
        for seg in conflict_segs:
            for seg_pt in seg:
                dist = np.linalg.norm(np.subtract(seg_pt, pt))
                if dist <= min_dist:
                    return False
        return True

    @staticmethod
    def make_pt(road, curve_id, t):
        x, y = road.curves[curve_id].t_to_point(t)
        return Road.Point(curve_id, t, x, y)

    @staticmethod
    def rnd_pt(rnd, road):
        return Road.make_pt(road, rnd.randint(0, 3), rnd.random())

    @staticmethod
    def clear_rnd_pt(rnd, road, is_clear_func, max_tries=10):
        for i in range(max_tries):
            pt = Road.rnd_pt(rnd, road)
            if is_clear_func(pt):
                return pt
        return None

    def build(self, b, params):
        l = float(params.get('l', 75.0))
        n = int(params.get('n', 4))
        cd = float(params.get('cd', 4))

        ref_road = self.build_ref_road(l)

        roads = [[] for x in range(4)]
        conflict_segs = []

        rnd = random.Random(0)
        is_clear_func = lambda pt: self.is_dist_away(pt, conflict_segs, ref_road, cd)
        endpt_func() = lambda from_road: self.clear_rnd_pt(rnd, ref_road, is_clear_func, )

        for i in range(n):
            start_pt = endpt_func()
            if start_pt is not None:
                end_pt = endpt_func()
                if end_pt is not None:
                    conflict_segs.append((start_pt, end_pt))

        print(conflict_segs)
        return None
