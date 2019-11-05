from pymonitor import *

class Monitor(PyMonitor):
    def get_description(self):
        return 'Monitor collisions between bounding boxes'
        
    def init(self):
        pass
            
    def step(self, frame, t, dt):
        # TODO, this is inefficient, we can use the bullet functionality to get only potentially interesting pairs
        for i, e1 in enumerate(self.scenario.entities):
            for j, e2 in enumerate(self.scenario.entities):
                if j > i:
                    if self.scenario.spatial_eng.detect_collision(e1, e2):
                        print (t, 'Collision detected: {}, {}'.format(e1.id, e2.id))
            