from spatial.spatial_component import SceneGraphNode
import util.math as umath


class LiDARSensor(SceneGraphNode):
    def __init__(self, scenario, mode_rotate):
        SceneGraphNode.__init__(self)
        self.spatial_eng = scenario.spatial_eng
        self.dbg_draw = scenario.dbg_draw
        self._matrix_s2p = umath.mat_transl(umath.vec_muls(scenario.coord.height_3d(), 2.0))
        self.mode_rot = mode_rotate
        self.dbg_draw_color = [0.4, 0, 0.95]
    
    def set_dbg_draw_color(self, rgb):
        self.dbg_draw_color = rgb
    
    def bind(self, car):
        pass

    def unbind(self, car):
        pass
    
    def sg_matrix_s2p(self):
        return self._matrix_s2p

    def step(self, t, dt):
        def to_deg_360(val):
            return val - (int(val/360.0) * 360.0)
        matrix_s2w = self.sg_matrix_s2w()
        origin = umath.mat_get_transl(matrix_s2w)
        if self.mode_rot:
            azimuth_center = to_deg_360(t * 360.0 * 4.0)
            azi_hfov = 15
            azi_res = 20
        else:
            azimuth_center = 0.0
            azi_hfov = 180
            azi_res = 60
        hits = self.spatial_eng.cast_rays_spherical(origin, 
                                umath.deg_rad(azimuth_center-azi_hfov), umath.deg_rad(azimuth_center+azi_hfov), azi_res,
                                umath.deg_rad(-20), umath.deg_rad(-2), 50, 500.0)
        self.dbg_draw.add_point_group([x[1] for x in hits], self.dbg_draw_color)
        