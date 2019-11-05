import random
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import scene
from util.arg import *

''' 
    TODO, check: https://github.com/fzi-forschungszentrum-informatik/Lanelet2/blob/master/lanelet2_core/doc/LaneletPrimitives.md
    https://wiki.openstreetmap.org/wiki/3D_development
    https://automating-gis-processes.github.io/CSC/notebooks/L3/retrieve_osm_data.html
'''

class RoadSideGen:
    def __init__(self, all_road_curves, coord, seed=0):
        self._all_road_curves = all_road_curves
        self._coord = coord
        self._rnd = random.Random(seed)
        
    def dist_pts_to_road(self, pts_road):
        return np.amin([self.dist_pt_to_road(x) for x in pts_road])
    def dist_pt_to_road(self, pt_road):
        return self.closest_pt_to_road(pt_road)[1]
    def closest_pts_to_road(self, pts_road):
        min_closest_pt = None
        min_dist = float('inf')
        for pt_road in pts_road:
            closest_pt_road, dist = self.closest_pt_to_road(curve, pt_road)
            if dist < min_dist:
                min_dist = min(dist, min_dist)
                min_closest_pt = closest_pt_road
        return min_closest_pt, min_dist
    def closest_pts_to_curve(self, curve, pts_road):
        min_dist = float('inf')
        min_closest_pt = None
        for pt_road in pts_road:
            closest_pt_road, dist = self.closest_pt_to_curve(curve, pt_road)
            if dist < min_dist:
                min_dist = min(dist, min_dist)
                min_closest_pt = closest_pt_road
        return min_closest_pt, min_dist
    def closest_pt_to_road(self, pt_road):
        min_dist = float('inf')
        min_closest_pt = None
        for curve in self.get_all_road_curves():    
            closest_pt_road, dist = self.closest_pt_to_curve(curve, pt_road)
            if dist < min_dist:
                min_dist = min(dist, min_dist)
                min_closest_pt = closest_pt_road
        return min_closest_pt, min_dist
    def closest_pt_to_curve(self, curve, pt_road):
        closest_t = curve.closest_t(pt_road)
        closest_pt_road = curve.t_to_point(closest_t)
        dist = np.linalg.norm(np.subtract(pt_road, closest_pt_road))
        return closest_pt_road, dist
    def dist_poly_to_curve(self, curve, poly_road):
        closest_pt_road, dist = self.closest_pts_to_curve(curve, poly_road)
        qry_point = Point(closest_pt_road) 
        qry_poly = Polygon(poly_road)
        return qry_poly.distance(qry_point)
    def dist_poly_to_road(self, poly_road):
        min_dist = float('inf')
        for curve in self._all_road_curves:
            dist = self.dist_poly_to_curve(curve, poly_road)
            min_dist = min(dist, min_dist)
        return min_dist    

    def gen_polys_road(self):
        double_sided = not arg_has('-single_sided')
        wild_place = arg_has('-wild_place')
        dbg_cand_i = int(arg_get('-dbg_cand_i', -1))
        polys_road = []
        poly_infos_road = []
        cand_i = 0
        for curve in self._all_road_curves:
            interval = 15.0
            depth_offsets = [5.0, 7.0]
            width_offsets = [-1.0, 1.0]
            widths = [8.0, 12.0]
            depths = [4.0, 10.0]
            min_dist_to_road = depth_offsets[0] * 0.8
            length = curve.get_length()
            place_count = int(length / interval)
            sides = [1.0, -1.0] if double_sided else [1.0]
            for side in sides:
                for place_i in range(place_count):
                    width = self._rnd.uniform(*widths)
                    depth = self._rnd.uniform(*depths)
                    depth_offset = self._rnd.uniform(*depth_offsets)
                    width_offset = self._rnd.uniform(*width_offsets)
                    t = float(place_i) / place_count
                    pt_curve = curve.t_to_point(t)
                    normal = np.multiply(curve.t_to_normal(t), side)
                    tang = curve.t_to_tangent(t)
                    anchor_road = np.add(pt_curve, np.multiply(normal, depth_offset))
                    anchor_road = np.add(anchor_road, np.multiply(tang, width_offset))
                    poly_road = [
                        np.add(anchor_road, np.multiply(tang, -width/2.0)),
                        np.add(anchor_road, np.multiply(tang, width/2.0)),
                        np.add(np.add(anchor_road, np.multiply(tang, width/2.0)), np.multiply(normal, depth)),
                        np.add(np.add(anchor_road, np.multiply(tang, -width/2.0)), np.multiply(normal, depth))
                    ]
                    
                    if dbg_cand_i != -1:
                        if cand_i != dbg_cand_i:
                            cand_i = cand_i + 1
                            continue
                    cand_i = cand_i + 1
                    
                    if wild_place or (self.dist_poly_to_road(poly_road) > min_dist_to_road):
                        polys_road.append((anchor_road, poly_road))
                        poly_center = np.multiply(np.add(poly_road[0], poly_road[2]), 0.5)
                        poly_infos_road.append((poly_center, curve.t_to_yaw(t), width, depth))
                        
        return polys_road, poly_infos_road
        
    def gen_polys_dbg_draw_lines_and_points(self):
        poly_dbg_draw_lines = []
        poly_dbg_draw_points = []
        polys_road, poly_infos_road = self.gen_polys_road()
        for anchor_road, poly_road in polys_road:
            anchor_world = self._coord.road_2d_to_spatial_3d_pt(anchor_road)
            poly_dbg_draw_points.append(anchor_world)
            
            poly_world = [self._coord.road_2d_to_spatial_3d_pt(x) for x in poly_road]
            for i in range(4):
                poly_dbg_draw_lines.append((poly_world[i], poly_world[(i+1)%4]))
        return poly_dbg_draw_lines, poly_dbg_draw_points
    
    def place_scene_boxes_from_polys(self, scenario, polys_road, poly_infos_road):
        heights = [15.0, 25.0]
        yaw_vec = self._coord.height_3d()
        for poly_center_road, yaw, width, depth in poly_infos_road:
            height = self._rnd.uniform(*heights)
            poly_center_world = self._coord.road_2d_to_spatial_3d_pt(poly_center_road)
            poly_center_world = self._coord.offset_height_3d(poly_center_world, height*0.5)
            scenario.place_scene_object(scene.SceneBox(pos=poly_center_world, orient_aa=yaw_vec+[yaw], lwh=[width,depth,height], rgb=[0.8,0.8,0.8]))

    def place_scene_boxes(self, scenario):
        polys_road, poly_infos_road = self.gen_polys_road()
        self.place_scene_boxes_from_polys(scenario, polys_road, poly_infos_road)