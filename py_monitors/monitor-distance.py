from pymonitor import *

class Monitor(PyMonitor):
    def get_description(self):
        return 'Monitor too-close distances between entities'
        
    def init(self):
        pass
            
    def step(self,  frame, t, dt):
        for i, e1 in enumerate(self.scenario.entities):
            for j, e2 in enumerate(self.scenario.entities):
                if j > i:
                    box_dist = self.scenario.spatial_eng.get_box_distance(e1, e2)
                    if box_dist < 2.0:
                        print (t, 'Too close ({}): {}, {}'.format(box_dist, e1.id, e2.id))
            