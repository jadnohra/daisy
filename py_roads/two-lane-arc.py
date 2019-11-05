from pyroad import *

class Road(PyRoad):

    def build(self, b, params):
        b.curve('A').start_at([0,0]).tangent_at_start([1,0]).end_at([100+10,110]).shape('arc')
        b.curve('Aa').start_at([0,10]).tangent_at_start([1,0]).end_at([100,110]).shape('arc')
        b.lane('A', 'Aa')