import random
from util.road import solve_lane_change_trajectory
from util.road import LaneChangeTrajectorySolution
from road.sequence_curve_builder import build_sampled_interpolation_curve

class WanderController:
    def __init__(self):
        self.rand = random.Random(0)
        self.curve_sequence = []
        self.min_planned_distance = 100.0
        self.curve_id_include_filter = None
        self.curve_id_exclude_filter = None
        self._command_change_lane = False

    def set_include_curve_id_filter(self, filter):
        self.curve_id_exclude_filter = None
        if filter is not None:
            self.curve_id_include_filter = set(filter)
        else:
            self.curve_id_include_filter = None

    def set_exclude_curve_id_filter(self, filter):
        self.curve_id_include_filter = None
        if filter is not None:
            self.curve_id_exclude_filter = set(filter)
        else:
            self.curve_id_exclude_filter = None

    def bind(self, car):
        self.car = car

    def unbind(self, car):
        self.car = None

    def _choose_successor(self, curve):
        candidates = curve.get_outgoing_curves()
        if self.curve_id_include_filter is not None:
            candidates = [x for x in candidates if x.id in self.curve_id_include_filter]
        if self.curve_id_exclude_filter is not None:
            candidates = [x for x in candidates if x.id not in self.curve_id_exclude_filter]
        if len(candidates):
            return candidates[self.rand.randint(0, len(candidates)-1)]
        return None

    def _add_tail_curve(self, curve):
        self._has_modifs = True
        self.curve_sequence.append(curve)

    def _remove_head_curves(self, n):
        if n > 0:
            self._has_modifs = True
            self.curve_sequence = self.curve_sequence[n:]

    def _reset_with_start_fragment(self, traj):
        self._has_modifs = True
        self._is_hard_modif = True
        self.curve_sequence = []
        for curve in traj:
            self._add_tail_curve(curve)

    def _sync_location(self):
        car_curve = self.car.location.curve
        for i, curve in enumerate(self.curve_sequence):
            if curve == car_curve:
                self._remove_head_curves(i)
                return
        self._reset_with_start_fragment([car_curve])

    def _get_tail(self):
        return None if len(self.curve_sequence) == 0 else self.curve_sequence[-1]

    def _calc_rest_distance(self):
        length = self.car.location.curve.dt_to_length(self.car.location.t,
                        1.0 - self.car.location.t)
        for curve in self.curve_sequence[1:]:
            length = length + curve.get_length()
        return length

    def command_change_lane(self):
        self._command_change_lane = True

    def _plan_lane_change(self, duration):
        target_lanes = self.car.location.curve.get_neighbor_lane_curves()
        if len(target_lanes) > 0:
            initial_target_lane = target_lanes[0]
            start_pt = self.car.spatial.pos_road
            speed = max(self.car.dynamics.get_speed(), 5.0)
            solution = solve_lane_change_trajectory(start_pt, initial_target_lane, speed, 2.0)
            if solution is not None:
                solution.link_to_last_target()
            return solution
        else:
            return None

    def _interpolate_lane_change(self, duration):
        loc = self.car.location
        target_lanes = loc.curve.get_neighbor_lane_curves()
        if len(target_lanes) > 0:
            initial_target_lane = target_lanes[0]
            start_pt = self.car.spatial.pos_road
            speed = max(self.car.dynamics.get_speed(), 5.0)
            end_t = loc.t + loc.curve.length_to_dt(loc.t, speed*duration)
            interp_curve = build_sampled_interpolation_curve(loc.curve, initial_target_lane, loc.t, end_t, loc.t, end_t)
            solution = LaneChangeTrajectorySolution()
            solution.link_to_last_target()
            return solution
        else:
            return None


    def _execute_commands(self):
        if self._command_change_lane:
            self._command_change_lane = False
            if True:
                #solution = self._plan_lane_change(2.0)
                solution = self._interpolate_lane_change(2.0)
                if solution is not None:
                    self._reset_with_start_fragment(solution.trajectory)
            else:
                self.car.act.set_mode(self.car.act.Mode.CHANGE_LANE)

    def step(self, t, dt):
        if self.car.location is None or self.car.location.curve is None:
            return
        # TODO: better design
        self._has_modifs = False
        self._is_hard_modif = False
        self._execute_commands()
        if self._is_hard_modif == False:
            self._sync_location()
        while self._calc_rest_distance() < self.min_planned_distance:
            last_curve = self._get_tail()
            if last_curve is None:
                break
            next_curve = self._choose_successor(last_curve)
            if next_curve is None:
                break
            self._add_tail_curve(next_curve)
        if self._has_modifs:
            if self._is_hard_modif:
                #print('reset', [x.id for x in self.curve_sequence])
                self.car.trajectory.reset_curve_sequence(self.curve_sequence)
            else:
                #print('update', [x.id for x in self.curve_sequence])
                self.car.trajectory.update_curve_sequence(self.curve_sequence)