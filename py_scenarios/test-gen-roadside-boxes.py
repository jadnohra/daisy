from pyscenario import *
from util.arg import *
from util.scene import RoadSideGen

class Scenario(PyScenario):
    def get_description(self):
        return 'Test random boxes at the border of roads'

    def get_map(self):
        return arg_get('-map', 'shapes-1')

    def init(self):
        gen = RoadSideGen(self.get_all_road_curves(), self.coord)
        gen.place_scene_boxes(self)