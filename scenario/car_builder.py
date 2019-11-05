import copy
from util.color import color_to_rgb
from component_base import ComponentBase
from scenario.road_location_component import RoadLocationComponent
from spatial.spatial_component import SpatialRoadPointLocationComponent
from models.kinematic_dynamics_model import KinematicDynamicsModel
from models.point_dynamics_model import PointDynamicsModel
from controllers.proximity_brake_controller import ProximityBrakeController
from controllers.act_controller import ActController
from controllers.wander_controller import WanderController
from sensors.lidar_sensor import LiDARSensor
from .road_trajectory_component import RoadTrajectoryComponent

class Car(ComponentBase):
    def __init__(self, id=None, rgb=[1,1,1], lwh=[4.4,1.7,1.4]):
        ComponentBase.__init__(self)
        self.id = id
        self.rgb = rgb
        self.lwh = lwh

class CarBuilder:
    def __init__(self, scenario, id=None):
        self._scenario = scenario
        self._controllers = set()
        self._sensors = []
        self.set_id(id)
    
    def set_id(self, id):
        self._id = id
        return self
        
    def set_dynamics(self, type):
        self._dynamics = type
        return self
        
    def set_color(self, rgb_or_name):
        self._rgb = color_to_rgb(rgb_or_name)
        return self
        
    def set_acceleration(self, val):
        self._acceleration = val
        return self
        
    def set_speed(self, val):
        self._speed = val
        return self
        
    def set_initial_speed(self, val):
        self._initial_speed = val
        return self

    def add_controller_by_name(self, name):
        self._controllers.add(name)
        return self

    def add_controller_wander(self):
        return self.add_controller_by_name('wa')
        
    def add_controller_proximity_brake(self):
        return self.add_controller_by_name('pb')
        
    def add_sensor_lidar(self, mode_rotate):
        self._sensors.append(('lidar', [mode_rotate]))
        return self
        
    def place(self, curve_id, curve_t=0.0):
        self._place_curve_id = curve_id
        self._place_curve_t = curve_t
        car = self.build()
        self._scenario.place_car(car)
        return car
        
    def build(self):
        id = self.get('id') if self.get('id', None) is not None else self._scenario._gen_car_id()
        car = Car(id=id, rgb=self.get('rgb', [1,1,1]))
        
        location = RoadLocationComponent()
        car.add_component('location', location)
        
        if self.has('place_curve_id'):
            car_curve = self._scenario.road.curve_table[self._place_curve_id]
            location.set(car_curve, self.get('place_curve_t', 0.0))
        
        if self.get('dynamics', 'point-dynamic') == 'point-dynamic':
            dynamics = PointDynamicsModel()
        else:
            dynamics = KinematicDynamicsModel()
        car.add_component('dynamics', dynamics)
        self._scenario.add_physics_stepper(dynamics)
        
        spatial_comp = SpatialRoadPointLocationComponent()
        car.add_component('spatial', spatial_comp)
        
        if self.has('acceleration'):
            dynamics.set_acceleration(self.get('acceleration'))
        
        if self.has('speed'):
            dynamics.set_speed(self.get('speed'))
        
        if self.has('initial_speed'):
            dynamics.set_initial_speed(self.get('initial_speed'))
        
        for ctrl_name in self._controllers:
            if ctrl_name == 'pb':
                controller = ProximityBrakeController(self._scenario)
                car.add_component(ctrl_name, controller)
                self._scenario.add_behavior_stepper(controller)
                
            elif ctrl_name == 'wa':
                car.add_component('trajectory', RoadTrajectoryComponent())
                
                wa_controller = WanderController()
                car.add_component(ctrl_name, wa_controller)
                
                act_controller = ActController()
                car.add_component('act', act_controller)
                
                # Implicit dependency simply by order of steppers in array
                self._scenario.add_behavior_stepper(wa_controller)
                self._scenario.add_behavior_stepper(act_controller)
                
        for sensor_name, sensor_cfg in self._sensors:
            if sensor_name == 'lidar':
                sensor = LiDARSensor(self._scenario, sensor_cfg[0])
                car.add_component('lidar', sensor)
                car.spatial.sg_add_child(sensor)
                self._scenario.add_sensor_stepper(sensor)
                
        return car
        
    def _attrname(self, key):
        return '_' + key

    def has(self, key):
        return hasattr(self, self._attrname(key))

    def get(self, key, dflt=None):
        name = self._attrname(key)
        return getattr(self, name) if hasattr(self, name) else dflt

    def set(self, key, value):
        name = self._attrname(key)
        setattr(self, name, value)