

class KinematicDynamicsModel:
    def __init__(self):
        self.set_speed(0)

    def set_speed(self, speed):
        self.speed = float(speed)

    def get_speed(self):
        return self.speed

    def get_target_speed(self):
        return self.speed

    def step(self, t, dt):
        pass

    def solve_eta_on_curve(self, curve, t_0, t_1):
        return self.solve_eta_on_curve_ex(curve, t_0, t_1, self.get_speed())

    def solve_eta_on_curve_ex(self, curve, t_0, t_1, speed):
        return solve_eta_on_curve_ex(curve, t_0, t_1, speed)
        
def solve_eta_on_curve_ex(curve, t_0, t_1, speed):
    ds = curve.dt_to_length(t_0, t_1-t_0)
    return ds / speed