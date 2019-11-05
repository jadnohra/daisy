from pyroad import *

class Road(PyRoad):
    def get_description(self):
        return 'A square divided into four squares'

    def get_asciiart(self):
        return \
'''
             |--K--|--I--|
             L     J     H
             |--C--|--G--|
             D     B     F
             |--A--|--E--|
'''

    def get_param_descriptions(self):
        return {'l':'Main length of roads (default: 75)'}

    def build(self, b, params):
        l = float(params.get('l', 75.0))
        b.curve('A').start_at([0,0]).length(l).angle(0)
        b.curve('B').start_at_end_of('A').length(l).angle(90)
        b.link('A', 'B')
        b.curve('C').start_at_end_of('B').length(l).angle(180)
        b.link('B', 'C')
        b.curve('D').start_at_end_of('C').length(l).angle(-90)
        b.link('C', 'D').link('D', 'A')

        b.curve('E').start_at_end_of('A').length(l).angle(0)
        b.link('A', 'E')
        b.curve('F').start_at_end_of('E').length(l).angle(90)
        b.link('E', 'F')
        b.curve('G').start_at_end_of('F').length(l).angle(180)
        b.link('F', 'G').link('G', 'C')

        b.curve('J').start_at_end_of('B').length(l).angle(90)
        b.link('B', 'J').link('G', 'J')
        b.curve('K').start_at_end_of('J').length(l).angle(180)
        b.link('J', 'K')
        b.curve('L').start_at_end_of('K').length(l).angle(-90)
        b.link('K', 'L').link('L', 'D')

        b.curve('H').start_at_end_of('F').length(l).angle(90)
        b.link('F', 'H')
        b.curve('I').start_at_end_of('H').length(l).angle(180)
        b.link('H', 'I').link('I', 'K')