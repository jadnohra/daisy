from pyroad import *

class Road(PyRoad):

    def build(self, b, params):
        b.curve('A').start_at([0,0]).tangent_at_start([1,0]).end_at([0,200]).shape('arc')