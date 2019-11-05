import os
from . import dbg_draw_3d_engine as deng
from road.road_builder import RoadBuilder
from road import road_convert
import scenario
import coord_xfm


class ObjDraw:
    def __init__(self):
        self.verts = []
        self.lines = []
        self.faces = []

    def load_file(self, road_module_or_file, road_params, use_mesh, use_polygons, lane_width):
        unproj = road_convert.CurveUnproj3D()
        center = True
        rd = RoadBuilder().load_and_build(road_module_or_file, road_params)
        vlo = road_convert.calc_road_obj_polylines(rd, unproj, center)
        self.verts, self.lines, self.offset = vlo[0], vlo[1], vlo[2]
        if use_mesh:
            vf = road_convert.centerlines_to_mesh_simple(self.verts, self.lines
                                                         , lane_width)
            self.verts, self.faces = vf[0], vf[1]
        elif use_polygons:
            vf = road_convert.centerlines_to_polygons(self.verts, self.lines
                                                         , lane_width)
            self.verts, self.faces = vf[0], vf[1]
        self.sliding = deng.vec_neg(self.offset)

    def draw(self, col_func):
        deng.scene_xfm_id()
        if self.faces:
            for face in self.faces:
                deng.scene_draw_vface(self.verts, face, deng.col_ylw, col_func)
        else:
            for line in self.lines:
                deng.scene_draw_vline(self.verts, line, deng.col_ylw, col_func)

def scene_road_update_file(sctx, road_file, road_params):
    scene = sctx['scene']
    opt_mesh = deng.arg_has('-mesh')
    opt_polygons = deng.arg_has('-polys')
    opt_lane_width = float(deng.arg_get('-lane_width', 10.0))
    if (sctx['frame'] == 0):
        scene['road'] = ObjDraw()
        scene['road'].load_file(road_file, road_params, opt_mesh, opt_polygons, opt_lane_width)
        scene['coord'] = coord_xfm.CoordXfm(scene['road'].sliding)
    return True


def scene_road_draw(sctx, col_func):
    scene = sctx['scene']
    scene['road'].draw(col_func)


def scene_scenario_update(sctx):
    return True


def scene_scenario_draw(sctx, col_func):
    scene = sctx['scene']
    coord = sctx['scene']['coord']
    viz_scale = float(deng.arg_get('-viz_scale', 1.0))
    if 'road' in scene:
        scene['road'].draw(col_func)
    if 'scenario' in scene:
        for entity in scene['scenario'].entities:
            if entity.has_component('spatial'):
                deng.scene_color_pass(*entity.rgb)
                deng.scene_xfm(entity.spatial.sg_matrix_s2p()) # TODO s2w, during scene-graph development
                deng.scene_draw_box(deng.vec_muls(entity.lwh, viz_scale))
    deng.scene_xfm_id()
    scene['scenario'].dbg_draw.flush(col_func)
