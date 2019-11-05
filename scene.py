from component_base import ComponentBase
from spatial.spatial_shape import SpatialBoxNode

class SceneBox(ComponentBase):
    def __init__(self, id=None, pos=[0,0,0], orient_aa=[1,0,0,0], lwh=[1,1,1], rgb=[1,1,1]):
        self.add_component('spatial', SpatialBoxNode(pos, orient_aa, lwh))
        self.id = id
        self.rgb = rgb
        self.lwh = lwh