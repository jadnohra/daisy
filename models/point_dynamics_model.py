import numpy as np


class PointDynamicsModel:
    def __init__(self):
        self.set_initial_speed(0)
        self.set_speed(0)
        self.set_acceleration(0)

    def set_initial_speed(self, speed):
        self.speed = float(speed)

    def set_speed(self, speed, event_acceleration = None):
        self.target_speed = float(speed)
        self.event_accel = event_acceleration

    def get_speed(self):
        return self.speed
        
    def get_target_speed(self):
        return self.target_speed

    def set_acceleration(self, accel):
        self.accel = float(accel)
        
    def get_acceleration(self):
        return self.event_accel if self.event_accel is not None else self.accel

    def reset_event_acceleration(self):
        self.event_accel = None

    def _step_speed(self, t, dt):
        accel = self.get_acceleration()
        ds = self.target_speed - self.speed
        da = max(min(ds / dt, accel), -accel)
        self.speed = self.speed + da * dt

    def step(self, t, dt):
        ds = self.target_speed - self.speed
        self._step_speed(t, dt)
        ds2 = self.target_speed - self.speed
        if np.sign(ds2) != np.sign(ds):
            self.reset_event_acceleration()

    def solve_eta_on_curve(self, curve, t_0, t_1):
        return self.solve_eta_on_curve_ex(curve, t_0, t_1, 
            self.get_speed(), self.get_target_speed(), self.get_acceleration())

    def solve_eta_on_curve_ex(self, curve, t_0, t_1, s_0, s_target, accel):
        return solve_eta_on_curve_ex(curve, t_0, t_1, s_0, s_target, accel)


def solve_eta_on_curve_ex(curve, t_0, t_1, s_0, s_target, accel):
    accel = np.abs(accel) if s_target > s_0 else -np.abs(accel)
    if s_target != s_0:
        Dt = (s_target - s_0) / accel
        Ds = 0.5 * accel * Dt * Dt + s_0 * Dt
    else:
        Dt = 0
        Ds = 0
    ds = curve.dt_to_length(t_0, t_1-t_0)
    if ds < Ds:
        roots = np.roots([0.5*accel, s_0, -ds])
        roots = [x for x in roots if np.isreal(x)]
        if len(roots):
            return np.amin(roots)
        else:
            return None
    else:
        return Dt + (ds - Ds) / s_target
