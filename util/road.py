from road.fragment_curve import FragmentCurve


class LaneChangeTrajectorySolution:
    def __init__(self, curve_sequence, last_target, last_target_solution):
        self.trajectory = curve_sequence
        self.last_target = last_target
        self.last_target_solution = last_target_solution

    def link_to_last_target(self):
        if self.last_target_solution.join_t is None:
            return
        last_cl_curve = self.trajectory[-1]
        if self.last_target_solution.join_t <= 1.0:
            frag_curve = FragmentCurve(self.last_target, self.last_target_solution.join_t, 1.0)
            last_cl_curve.add_outgoing_curve(frag_curve)
            self.trajectory.append(frag_curve)
        last_cl_curve = self.trajectory[-1]
        for curve in self.last_target.get_outgoing_curves():
            last_cl_curve.add_outgoing_curve(curve)


def solve_lane_change_trajectory(start_pt, first_target_lane_curve, speed, lane_change_duration):
    cuve_sequence = []
    next_target_curve = first_target_lane_curve
    next_start_pt = start_pt
    next_duration = lane_change_duration
    while True:
        last_target_solution = next_target_curve.solve_lane_change_curve(next_start_pt, speed, next_duration)
        if last_target_solution is None:
            return None
        lc_curve = last_target_solution.curve
        if lc_curve is not None:
            if len(cuve_sequence):
                prev_curve = cuve_sequence[-1]
                prev_curve.add_outgoing_curve(lc_curve)
                lc_curve.add_incoming_curve(prev_curve)
            cuve_sequence.append(lc_curve)
        if last_target_solution.status == 'chain':
            if len(next_target_curve.get_outgoing_curves()) == 1: # TODO, support multiple
                next_target_curve = next_target_curve.get_outgoing_curves()[0]
                if lc_curve is not None:
                    next_start_pt = lc_curve.t_to_point(1)
                    next_duration = max(next_duration - (lc_curve.get_length()  / speed), 0.1)
            else:
                return None
        else:
            break
    return LaneChangeTrajectorySolution(cuve_sequence, next_target_curve, last_target_solution)

