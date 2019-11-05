import util.math as umath
from .spatial_component import SceneGraphNode, SpatialBulletComponentBase

class SpatialBoxNode(SceneGraphNode, SpatialBulletComponentBase):
    def __init__(self, pos, orient_aa, lwh):
        SceneGraphNode.__init__(self)
        SpatialBulletComponentBase.__init__(self)
        self.lwh = lwh
        self.set_pose(pos, orient_aa)
        
    def set_pose(self, pos, orient_aa):
        self.pos = pos
        self.orient_aa = orient_aa
        self._matrix_s2p = umath.mat_transl_aa(pos, orient_aa)
        self._is_dirty = True
        # This is wrong, move it to worl matrix update, and use dirty flags correctly
        if self.has_bullet_object() == False:
            self.create_bullet_object(self.pos, self.orient_aa, self.lwh)
        else:
            self.teleport_bullet_object(self.pos, self.orient_aa)
        
    def sg_matrix_s2p(self):
        return self._matrix_s2p