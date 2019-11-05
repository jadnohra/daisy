from pyroad import *

class Road(PyRoad):

    def build(self, b, params):
        b.curve('A').start_at([5,5]).length(25)
        b.curve('B').start_at_end_of('A').end_at([25,50]).shape('arc')
        b.link('A', 'B')