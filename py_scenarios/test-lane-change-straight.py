from pyscenario import *
from util.arg import *
from util.road import solve_lane_change_trajectory
from road.road_builder import RoadBuilder


class Scenario(PyScenario):
    def get_description(self):
        return 'Test for straight lane change solver'

    def get_map(self):
        return arg_get('-map', 'two-lane-triangle')

    def get_map_parameters(self):
        return {'s':'straight', 'o':5, 'd':0.3}

    def init(self):
        self.next_trigger_time = 1.0
        self.car_1 = self.build_car().set_acceleration(40) \
                                .set_speed(30) \
                                .add_controller_wander() \
                                .place('A', 0.0)

    def step(self, frame, t, dt):
        if t > self.next_trigger_time:
            self.car_1.wa.command_change_lane()
            self.next_trigger_time = t + 2.0
        '''
        neighbor_lane_curves = self.car_1.location.curve.get_neighbor_lane_curves()
        if len(neighbor_lane_curves) > 0:
            initial_target_lane = neighbor_lane_curves[0]
            start_pt = self.car_1.spatial.pos_road
            speed = max(self.car_1.dynamics.get_speed(), 10.0)
            solution = solve_lane_change_trajectory(start_pt, initial_target_lane, speed, 2.0)
            if solution is not None and solution.trajectory is not None:
                self.dbg_draw.add_trajectory(solution.trajectory)
        '''

