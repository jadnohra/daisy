import os
import numpy as np
from OpenGL.GL import glPushMatrix, glPopMatrix, glTranslatef
from scenario.car_builder import CarBuilder
from util.module import make_class_instance
import util.logging as logging
from road.road_builder import RoadBuilder
from road.road_convert import calc_curve_segments, curve_segments_to_vert_pair_list
from spatial import spatial_engine
from stepping import SteppingScheduler
import dbg_draw.dbg_draw_3d_engine as dbg_draw_eng
from pyparam import g_param

class PyScenario:
    
    class DbgDraw:
        def __init__(self, coord):
            self.coord = coord
            self.points = []
            self.point_groups = []
            self.lines = []
            self.line_groups = []
        
        def add_point(self, pos):
            self.points.append(pos)
        
        def add_point_group(self, points, rgb, ttl=0.0):
            self.point_groups.append((points, rgb, ttl))
        
        def add_line(self, pt_from, pt_to):
            self.lines.append((pt_from, pt_to))
            
        def add_line_group(self, lines_endpoints, rgb, ttl=0.0):
            if len(lines_endpoints):
                self.line_groups.append((lines_endpoints, rgb, ttl))
            
        def add_sampled_trajectory(self, trajectory, rgb, seg_length=2.0, ttl=0.0):
            sampled_pts = [self.coord.road_2d_to_spatial_3d_pt(x) for x in trajectory.sample_pts(seg_length)]
            print('WWWW', sampled_pts)
            self.add_point_group(sampled_pts, rgb, ttl)
            
        def add_trajectory(self, trajectory, ttl=0.0, sampled=False):
            curve_verts = []
            for i, curve in enumerate(trajectory):
                verts = []; lines = [];
                # TODO optimize
                calc_curve_segments(curve, verts, lines, vert_func=self.coord.road_2d_to_spatial_3d_pt)
                curve_verts.extend(curve_segments_to_vert_pair_list(verts, lines))
            self.add_line_group(curve_verts, [1.0, 0.0, 1.0], ttl)
            
        def clear(self):
            self.points.clear()
            ttl_point_groups = [(x[0], x[1], x[2]-1) for x in self.point_groups if x[2] > 1]
            self.point_groups.clear()
            self.point_groups = ttl_point_groups
            self.lines.clear()
            ttl_line_groups = [(x[0], x[1], x[2]-1) for x in self.line_groups if x[2] > 1]
            self.line_groups.clear()
            self.line_groups = ttl_line_groups
            
        def flush(self, col_func):
            rgb_white = [1,1,1]
            col_func(*rgb_white)
            # dbg_draw_eng.scene_draw_lines(self.points, dim=5.0)
            dbg_draw_eng.scene_draw_points_pos(self.points, dim=5.0)
            for pts, rgb, ttl in self.point_groups:
                col_func(*rgb)
                dbg_draw_eng.scene_draw_points_pos(pts, dim=5.0)
            col_func(*rgb_white)
            dbg_draw_eng.scene_draw_lines(self.lines)
            for lines, rgb, tll in self.line_groups:
                col_func(*rgb)
                dbg_draw_eng.scene_draw_lines(lines)
        
    DYNAMICS_KINEMATIC, DYNAMICS_POINT = range(2)
    
    def get_map(self):
        return ''
    
    def get_map_parameters(self):
        return {}
    
    def get_description(self):
        return ''
    
    def init(self):
        pass
    
    def _get_map(self):
        return self.get_map()
    
    def _get_map_parameters(self):
        return self.get_map_parameters()
    
    def _init(self, coord):
        def load_road():
            self.road = RoadBuilder().load_and_build(self._get_map(), self._get_map_parameters())
            logging.info(f"road: {self.road.source}")
            if len(self.road.description):
                logging.info(" " + self.road.description)
            if len(self.road.asciiart):
                logging.info(" " + self.road.asciiart)
            if len(self.road.param_descriptions):
                logging.info(" " + str(self.road.param_descriptions))
            if len(self.road.params):
                logging.info(" " + str(self.road.params))
        self.coord = coord
        self.dbg_draw = self.DbgDraw(self.coord)
        self.physics_steppers = set()
        self.sensor_steppers = set()
        self.behavior_steppers = set()
        self.stepping_sched = SteppingScheduler()
        load_road()
        self.entities = set()
        self.car_entities = set()
        self.car_ids = {}
        self.spatial_eng = spatial_engine.SpatialEngine(self.entities, self.coord)
        self.spatial_eng.add_ground_plane(10000) 
        self.auto_car_id_counter = 0
        self.init()
        

    def _gen_car_id(self):
        id = '#' + str(self.auto_car_id_counter)
        self.auto_car_id_counter = self.auto_car_id_counter + 1
        return id
    
    def _step_physics(self, t, dt):
        for stepper in self.physics_steppers:
            stepper.step(t, dt)
            
    def _step_sensors(self, t, dt):
        for stepper in self.sensor_steppers:
            stepper.step(t, dt)
            
    def _step_behaviors(self, t, dt):
        for stepper in self.behavior_steppers:
            stepper.step(t, dt)
    
    def _update_steppers(self, t, dt):
        self.dbg_draw.clear()
        self._step_physics(t, dt)
        self.spatial_eng.step(t, dt)
        self._step_sensors(t, dt)
        self._step_behaviors(t, dt)

    def _step(self, frame, t, dt):
        self._update_steppers(t, dt)
        self.step(frame, t, dt)
    
    def step(self, frame, t, dt):
        pass
    
    def add_physics_stepper(self, stepper):
        self.physics_steppers.add(stepper)

    def remove_physics_stepper(self, stepper):
        self.phsyics_steppers.remove(stepper)
    
    def build_car(self, id=None):
        return CarBuilder(self, id=id)

    def place_car(self, car):
        self.entities.add(car)
        self.car_entities.add(car)

    def add_sensor_stepper(self, stepper):
        self.sensor_steppers.add(stepper)

    def remove_sensor_stepper(self, stepper):
        self.sensor_steppers.remove(stepper)
        
    def add_behavior_stepper(self, stepper):
        self.behavior_steppers.add(stepper)

    def remove_behvior_stepper(self, stepper):
        self.behavior_steppers.remove(stepper)
        
    def get_road_curve(self, curve_id):
        return self.road.curve_table.get(curve_id, None)

    def get_all_road_curves(self):
        return self.road.curves

    def get_first_road_curve_id(self):
        return self.get_all_road_curves()[0].id

    def place_scene_object(self, object):
        self.entities.add(object)
