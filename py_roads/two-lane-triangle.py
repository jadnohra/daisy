from pyroad import *
from road.road_builder import RoadBuilder
import numpy as np

class Road(PyRoad):
    def get_description(self):
        return 'A two-lane triangle'

    def get_asciiart(self):
        return \
'''
                  E
                // \\\\
                C   B
              //     \\\\
            F//===A===\\\\D
'''

    def get_param_descriptions(self):
        return {'l':'Main length of roads (default: 100)',
                'd':'Delta of normalized length to shave off for curved corners (default: 0.2)',
                'o':'Offset of lanes (default: 2)',
                's':'Curve type at shoulders (default: arc)'
                }

    # Build a basic triangle with no arcs
    def build_ref_road(self, l):
        b = RoadBuilder()
        b.curve('A').start_at([0,0]).length(l)
        b.curve('B').start_at_end_of('A').length(l).angle(120)
        b.curve('C').start_at_end_of('B').length(l).angle(120+120)
        return b.build()

    def get_verts(self, ref, curve, r):
        curve = ref.curve_table[curve]
        return [curve.t_to_point(0.0+r), curve.t_to_point(1.0-r)]

    def offset_verts(self, ref, curve, verts, off):
        curve = ref.curve_table[curve]
        off_vecs = [np.multiply(curve.t_to_normal(x), off) for x in [0,1]]
        return [np.add(verts[i], off_vecs[i]) for i in range(2)]

    def build(self, b, params):
        l = float(params.get('l', 100.0))
        d = float(params.get('d', 0.2))
        o = float(params.get('o', 2.0))
        s = str(params.get('s', 'arc'))
        ref = self.build_ref_road(l)

        # Inner triangle straight parts
        A_p, A_q = self.get_verts(ref, 'A', d)
        b.curve('A').start_at(A_p).end_at(A_q)
        b.curve('A').start_at(A_p).end_at(A_q)
        B_p, B_q = self.get_verts(ref, 'B', d)
        b.curve('B').start_at(B_p).end_at(B_q)
        C_p, C_q = self.get_verts(ref, 'C', d)
        b.curve('C').start_at(C_p).end_at(C_q)

        # Inner triangle arcs
        b.curve('D').start_at_end_of('A').end_at_start_of('B').shape(s)
        b.link('A', 'D').link('D', 'B')
        b.curve('E').start_at_end_of('B').end_at_start_of('C').shape(s)
        b.link('B', 'E').link('E', 'C')
        b.curve('F').start_at_end_of('C').end_at_start_of('A').shape(s)
        b.link('C', 'F').link('F', 'A')

        # Outer triangle straight parts
        Aa_p, Aa_q = self.offset_verts(ref, 'A', [A_p, A_q], -o)
        b.curve('Aa').start_at(Aa_p).end_at(Aa_q)
        Ba_p, Ba_q = self.offset_verts(ref, 'B', [B_p, B_q], -o)
        b.curve('Ba').start_at(Ba_p).end_at(Ba_q)
        Ca_p, Ca_q = self.offset_verts(ref, 'C', [C_p, C_q], -o)
        b.curve('Ca').start_at(Ca_p).end_at(Ca_q)

        # Outer triangle curves
        b.curve('Da').start_at_end_of('Aa').end_at_start_of('Ba').shape(s)
        b.link('Aa', 'Da').link('Da', 'Ba')
        b.curve('Ea').start_at_end_of('Ba').end_at_start_of('Ca').shape(s)
        b.link('Ba', 'Ea').link('Ea', 'Ca')
        b.curve('Fa').start_at_end_of('Ca').end_at_start_of('Aa').shape(s)
        b.link('Ca', 'Fa').link('Fa', 'Aa')
        
        # lanes
        for name in ['A', 'B', 'C', 'D', 'E', 'F']:
            b.lane(name, name+'a')
            