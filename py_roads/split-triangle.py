from pyroad import *

class Road(PyRoad):
    def get_description(self):
        return 'A Triangle split in two'
        
    def get_asciiart(self):
        return \
'''               
                /  |  \\
               D   C   E
              /    |    \\
             /--A--|--B--\\
'''

    def get_param_descriptions(self):
        return {'l':'Main length of roads (default: 75)'}
        
    def build(self, b, params):
        l = float(params.get('l', 75.0))
        b.curve('A').start_at([0,0]).length(l)
        b.curve('B').start_at_end_of('A').length(l)
        b.link('A', 'B')
        b.curve('C').start_at_end_of('A').length(1.5*l).angle(90)
        b.link('A', 'C')
        
        b.curve('D').start_at_end_of('C').end_at_start_of('A')
        b.link('C', 'D').link('D', 'A')
        
        b.curve('E').start_at_end_of('B').end_at_end_of('C')
        b.link('B', 'E').link('E', 'D')
