from pyscenario import *
import util.scenario


class Scenario(PyScenario):
    def get_description(self):
        return 'Test spatial FOV functionality'
        
    def get_map(self):
        return 'four-square'
        
    def init(self):
        util.scenario.add_random_cars(self, 20, component_names=['wa'])
        filter = set(['A', 'B', 'C', 'D', 'J', 'K', 'L'])
        for car in self.car_entities:
            if car.location.curve.id in filter:
                car.rgb=[0,0,1]
                car.wa.set_include_curve_id_filter(filter)
            else:
                car.rgb=[1,0,0]
                car.wa.set_exclude_curve_id_filter(filter)