from pyroad import *

class Road(PyRoad):

    def build(self, b, params):
        b.curve('A').start_at([0,0]).length(75).angle(0)
        b.curve('B').start_at([0,0]).length(75).angle(190)
        b.curve('C').start_at([0,0]).tangent_at_start([1,0]).end_at([10,50]).shape('arc')