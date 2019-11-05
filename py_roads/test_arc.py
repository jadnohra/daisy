from pyroad import *

class Road(PyRoad):

    def build(self, b, params):
        b.curve('A').start_at([0,0]).tangent_at_start([1,1]).end_at([0,100]).shape('arc')

        b.curve('B').start_at([0,0]).end_at([100,0])
        b.curve('C').start_at_end_of('B').end_at([100,100]).shape('arc')