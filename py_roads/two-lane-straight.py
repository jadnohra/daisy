from pyroad import *

class Road(PyRoad):

    def build(self, b, params):
        b.curve('A').start_at([5,5]).length(150)
        b.curve('Aa').start_at([5,15]).length(150)
        b.lane('A', 'Aa')