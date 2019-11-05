from pyscenario import *
from util.arg import *
from road.road_builder import RoadBuilder


class Scenario(PyScenario):
    def get_description(self):
        return 'A car, changing lanes, with another car speeding around it with proximity-brake'
        
    def get_map(self):
        return arg_get('-map', 'two-lane-triangle')

    def init(self):
        self.next_trigger_time = 1.0
        self.car_1 = self.build_car().set_acceleration(40) \
                                .set_speed(30) \
                                .add_controller_wander() \
                                .place('A', 0.0)

    def step(self, frame, t, dt):
        if t > self.next_trigger_time:
            loc = self.car_1.location
            start_pt = self.car_1.spatial.pos_road
            neighbor_lane_curves = loc.curve.get_outgoing_lane_curves() + loc.curve.get_incoming_lane_curves()
            if len(neighbor_lane_curves) > 0:
                neighbor_curve = neighbor_lane_curves[0]
                offset_t = neighbor_curve.length_to_dt(loc.t, 12.0)
                target_t = loc.t + offset_t
                if target_t <= 1.0 and not neighbor_curve.is_curved(): # TODO support this case
                    # TODO support arc as change-lane curve
                    self.next_trigger_time = self.next_trigger_time + 2.0
                    end_pt = neighbor_curve.t_to_point(target_t)
                    b = RoadBuilder()
                    b.curve().start_at(start_pt).end_at(end_pt)
                    r = b.build()
                    change_lane_curve = r.curves[0]
                    change_lane_curve.set_target_curve_loc(neighbor_curve, target_t)
                    change_lane_curve.id = None
                    loc.set_location(change_lane_curve, 0.0) # TODO This is a hack, we need the location to notify the wanderer (listener)
        if True:
            loc = self.car_1.location
            start_pt = self.car_1.spatial.pos_road
            neighbor_lane_curves = loc.curve.get_outgoing_lane_curves() + loc.curve.get_incoming_lane_curves()
            if len(neighbor_lane_curves) > 0:
                neighbor_curve = neighbor_lane_curves[0]
                lc_curve = neighbor_curve.solve_lane_change_curve(start_pt, self.car_1.dynamics.get_speed(), 2.0)
                if (lc_curve is not None) and (not lc_curve.is_curved()):
                    road_pts = [lc_curve.t_to_point(0), lc_curve.t_to_point(1)]
                    world_pts = [self.coord.road_2d_to_spatial_3d_pt(x) for x in  road_pts]
                    self.dbg_draw.add_line_group([world_pts], [1.0, 0.0, 1.0])
                
