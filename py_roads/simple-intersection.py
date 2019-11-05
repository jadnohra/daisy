'''
curve id=A at=(0, 400) length=400 angle=0
curve id=Aa at=(end of A) length=400 angle=0
link A -> Aa
curve id=B at=(400, 0) length=400 angle=90
link B -> Aa
'''

from pyroad import *

class Road(PyRoad):

    def build(self, b, params):
        b.curve('A').start_at([0,0]).length(400)
        b.curve('Aa').start_at_end_of('A').length(400)
        b.link('A', 'Aa')
        b.curve('B').end_at_start_of('Aa').length(400).angle(90)
        b.link('B', 'Aa')