from pyroad import *

class Road(PyRoad):

    def build(self, b, params):
        b.curve('A').start_at([5,5]).length(400).angle(190)