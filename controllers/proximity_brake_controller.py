import numpy as np
from statemachine import StateMachine, State


class ProximityBrakeController:
    
    class BrakeEventStateMachine(StateMachine):
        idle = State('Idle', initial=True)
        triggered = State('Triggered')
        
        brake = idle.to(triggered)
        to_idle = triggered.to(idle)

        def __init__(self, comp):
            StateMachine.__init__(self)
            self.comp = comp
        
        def on_enter_triggered(self):
            self.pre_brake_speed = self.comp.car.dynamics.get_target_speed()
            self.comp.car.dynamics.set_speed(0, event_acceleration=self.comp.brake_accel)
    
        def on_exit_triggered(self):
            self.comp.car.dynamics.set_speed(self.pre_brake_speed)
    
    def __init__(self, scenario):
        self.spatial_eng = scenario.spatial_eng
        self.car_entities = scenario.car_entities
        self.trigger_radius = 6
        self.trigger_fov = np.deg2rad(30)
        self.brake_accel = 1500
        self.sm = None
        
    def bind(self, car):
        self.car = car
        self.sm = self.BrakeEventStateMachine(self)

    def unbind(self, car):
        self.car = None
        self.sm = None
        
    def has_entities_in_fov(self):
        ents_fov = self.spatial_eng.get_entities_in_fov(self.car, self.trigger_radius, self.trigger_fov, self.car_entities)
        return len(ents_fov) > 0
        
    def step(self, t, dt):
        if self.sm.is_idle:
            if self.car.dynamics.get_speed() != 0 and self.has_entities_in_fov():
                self.sm.brake()
        else:
            if self.car.dynamics.get_speed() == 0 and self.has_entities_in_fov() == False:
                self.sm.to_idle()