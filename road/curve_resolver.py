import numpy as np
from .straight_curve import StraightCurve
from .arc_curve import ArcCurve
from util.math import intersect_two_lines

class CurveResolver:
    def __init__(self, builder):
        self.builder = builder
        self.id = self.builder.get('id', None)
        self.rgb = self.builder.get('rgb',[1, 1, 1])
        self.shape = self.builder.get('shape', None)
        self.world_start = None
        self.world_end = None
        self.resolved_curve = None

    def is_resolved(self):
        return self.get_resolved() is not None

    def get_resolved(self):
        return self.resolved_curve

    def resolve(self, curve_table):
        def resolve_point(builder, curve_table, key_pos, key_rel, key_t, curve, attr_name, info_key):
            if builder.has(key_pos) or self.builder.has(key_rel):
                if builder.has(key_pos):
                    setattr(curve, attr_name, builder.get(key_pos))
                else:
                    rel_seg_id = builder.get(key_rel)
                    if rel_seg_id not in curve_table:
                        raise Exception(f"Curve '{curve.id}' references inexistent curve '{rel_seg_id}'")
                    if rel_seg_id in curve_table and \
                       curve_table[rel_seg_id].is_resolved():
                        rel_seg_t = builder.get(key_t)
                        setattr(curve, attr_name, \
                            curve_table[rel_seg_id].get_resolved().t_to_point(rel_seg_t))
                    else:
                        return False
            else:
                raise Exception(f"Curve '{curve.id}' has no '{info_key}' information")
            return True
        def resolve_tangent(builder, curve_table, key_tangent, key_rel, key_t, my_id):
            if builder.has(key_tangent) or self.builder.has(key_rel):
                if builder.has(key_tangent):
                    return True
                else:
                    rel_seg_id = builder.get(key_rel)
                    if rel_seg_id in curve_table and \
                       curve_table[rel_seg_id].is_resolved():
                        rel_seg_t = builder.get(key_t)
                        builder.set(key_tangent, \
                            curve_table[rel_seg_id].get_resolved().t_to_tangent(rel_seg_t))
                    else:
                        return False
            else:
                raise Exception(f"Curve '{my_id}' has no tangent information")
            return True
        def vec_to_angle(vec):
            a = np.arctan2(vec[1], vec[0])
            return a + 2.0*np.pi if a < 0.0 else a
        def delta_to_respect_tangent(curve, tang, t, delta):
            tang_dot = np.dot(tang, curve.t_to_tangent(t))
            if tang_dot < 0.0:
                return delta - np.sign(delta) * 2.0 * np.pi
            else:
                return delta
        def resolve_start_point(curve_table, curve):
            return resolve_point(curve.builder, curve_table, \
                'start_at_pos', 'start_at_rel', 'start_at_t', curve, \
                'world_start', 'start')
        def resolve_end_point(curve_table, curve):
            return resolve_point(curve.builder, curve_table, \
                    'end_at_pos', 'end_at_rel', 'end_at_t', curve, \
                    'world_end', 'end')
        if self.is_resolved():
            return self.get_resolved()
        if self.world_start is None:
            if self.builder.has('start_at_pos') or self.builder.has('start_at_rel'):
                if not resolve_start_point(curve_table, self):
                    return None
            else:
                if self.builder.has('end_at_pos') or self.builder.has('end_at_rel'):
                    if self.builder.has('length'):
                        if not resolve_end_point(curve_table, self):
                            return None
                        self.length = self.builder.get('length')
                        angle = self.builder.get('angle', 0.0)
                        dir_vec = [np.cos(angle), np.sin(angle)]
                        len_vec = np.multiply(dir_vec, self.length)
                        self.dir_vec = dir_vec
                        self.world_start = np.subtract(self.world_end, len_vec)
                    else:
                        raise Exception(f"Curve '{my_id}' has no length information")
                else:
                    raise Exception(f"Curve '{my_id}' has no endpoint information")
        if self.world_end is None:
            if self.builder.has('length'):
                self.length = self.builder.get('length')
                angle = self.builder.get('angle', 0.0)
                dir_vec = [np.cos(angle), np.sin(angle)]
                len_vec = np.multiply(dir_vec, self.length)
                self.dir_vec = dir_vec
                self.world_end = np.add(self.world_start, len_vec)
            else:
                if not resolve_end_point(curve_table, self):
                    return None
                len_vec = np.subtract(self.world_end, self.world_start)
                self.length = np.linalg.norm(len_vec)
                self.dir_vec = np.multiply(len_vec, 1.0/self.length)
        if self.shape is None or self.shape == 'straight':
            self.resolved_curve = StraightCurve(self.id, self.rgb, 
                                                self.world_start, self.world_end)
            return self.resolved_curve
        elif self.shape == 'arc':
            if ((not resolve_tangent(self.builder, curve_table, 'tangent_at_start', 'start_at_rel', 'start_at_t', self.id))
                    and
                    (not resolve_tangent(self.builder, curve_table, 'tangent_at_start', 'end_at_rel', 'end_at_t', self.id))
                    ):
                return None
            if self.builder.has('tangent_at_start'):
                tang = self.builder.get('tangent_at_start')
                line_T = (self.world_start, [-tang[1], tang[0]])
            else: # self.builder.has('tangent_at_end'):
                tang = self.builder.get('tangent_at_end')
                line_T = (self.world_end, [-tang[1], tang[0]])
            line_N_vec = np.subtract(self.world_end, self.world_start)
            line_N = (list(np.multiply(np.add(self.world_start, self.world_end), 0.5)),
                      [-line_N_vec[1], line_N_vec[0]])
            center_t = intersect_two_lines(line_N, line_T)[0]
            center = np.add(line_N[0], np.multiply(line_N[1], center_t))
            radius = np.linalg.norm(np.subtract(self.world_start, center))
            self.world_arc_center = center
            self.arc_rad = radius
            edge_vecs = (np.subtract(self.world_start, center), np.subtract(self.world_end, center))
            edge_angles = [vec_to_angle(x) for x in edge_vecs]
            self.arc_angle_start = edge_angles[0]
            self.arc_angle_end = edge_angles[1]
            self.arc_path_delta = self.arc_angle_end - self.arc_angle_start
            test_curve = ArcCurve(self.id, self.rgb, 
                                            self.world_start, self.world_end,
                                            self.world_arc_center, self.arc_rad,
                                            self.arc_angle_start, self.arc_angle_end,
                                            self.arc_path_delta)
            if self.builder.has('tangent_at_start'):
                self.arc_path_delta = delta_to_respect_tangent(
                                        test_curve,
                                        self.builder.get('tangent_at_start'),
                                        0.0,
                                        self.arc_path_delta)
                #TODO warn if tangent at other side has a large mismatch
            else: #if self.builder.has('tangent_at_start'):
                self.arc_path_delta = delta_to_respect_tangent(
                                        test_curve,
                                        self.builder.get('tangent_at_end'),
                                        1.0,
                                        self.arc_path_delta)
            self.resolved_curve = ArcCurve(self.id, self.rgb, 
                                            self.world_start, self.world_end,
                                            self.world_arc_center, self.arc_rad,
                                            self.arc_angle_start, self.arc_angle_end,
                                            self.arc_path_delta)
            return self.resolved_curve
        else:
            raise Exception(f"Curve '{self.id}' has invalid shape '{self.shape}'")
