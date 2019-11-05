from pyscenario import *

class Scenario(PyScenario):
    def get_description(self):
        return 'Test closest point on road curve query'

    def get_map(self):
        return 'shapes-1'

    def step(self, frame, t, dt):
        test_pt_road = np.multiply([np.cos(t), np.sin(t)], 50.0)
        test_pt_world = self.coord.road_2d_to_spatial_3d_pt(test_pt_road)
        self.dbg_draw.add_point(test_pt_world)

        for curve in self.get_all_road_curves():
            closest_t = curve.closest_t(test_pt_road)
            closest_pt_road = curve.t_to_point(closest_t)
            closest_pt_world = self.coord.road_2d_to_spatial_3d_pt(closest_pt_road)
            self.dbg_draw.add_point(closest_pt_world)
            self.dbg_draw.add_line(test_pt_world, closest_pt_world)

