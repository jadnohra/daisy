import pybullet as bullet
import numpy as np
import util.math as umath


class SpatialBulletComponentBase:
    def __init__(self):
        self.bid = -1
        self._coll_shape = None
        
    def has_bullet_object(self):
        return self.bid != -1

    def remove_bullet_object(self):
        if (self.bid != -1):
            bullet.removeBody(self.bid)
            bullet.removeCollisionShape(self._coll_shape)
            self.bid = -1
            
    def orient_to_bullet_quat(self, orient_aa):
        rvec = [x*orient_aa[3] for x in orient_aa[:3]]
        return bullet.getQuaternionFromEuler(rvec)
            
    def create_bullet_object(self, pos, orient_aa, lwh):
        if (self.bid == -1):
            orient = self.orient_to_bullet_quat(orient_aa)
            self._coll_shape = bullet.createCollisionShape(bullet.GEOM_BOX, halfExtents=np.multiply(lwh, 0.5))
            self.bid = bullet.createMultiBody(baseMass=0,
                                            baseCollisionShapeIndex=self._coll_shape,
                                            basePosition=pos,
                                            baseOrientation=orient)

    def teleport_bullet_object(self, pos, orient_aa):
        orient = self.orient_to_bullet_quat(orient_aa)
        bullet.resetBasePositionAndOrientation(self.bid, pos, orient)


class SceneGraphNode:

    _mat_id = umath.mat_id()

    def __init__(self):
        self._children = set()
        self._is_dirty = True

    def sg_is_internal(self):
        return not is_leaf()

    def sg_is_leaf(self):
        return len(self._children) == 0

    def sg_children(self):
        return self._children

    def sg_set_children(self, children):
        self._children = set(children)

    def sg_add_child(self, child):
        self._children.add(child)

    def sg_add_children(self, children):
        for child in children:
            self.add_child(child)

    def sg_sort_children(self):
        self._children = sorted(self._children, key= lambda x: x.name())

    def sg_is_dirty(self):
        return self._is_dirty
        
    def sg_reset_dirty(self):
        self._is_dirty = False
        
    def sg_update_matrix_world(self, parent):
        if parent is not None:
            self._cached_s2w = umath.mat_mul(parent.sg_matrix_s2w(), self.sg_matrix_s2p())
        else:
            self._cached_s2w = self.sg_matrix_s2p()
        
    def sg_update_matrix_self(self, coord):
        pass
        
    # s2p stands for self-to-parent
    def sg_matrix_s2p(self):
        return _mat_id
    
    # s2w stands for self-to-world
    def sg_matrix_s2w(self):
        return self._cached_s2w


class SpatialRoadPointLocationComponent(SceneGraphNode, SpatialBulletComponentBase):
    def __init__(self):
        SceneGraphNode.__init__(self)
        SpatialBulletComponentBase.__init__(self)
        self._matrix_s2p = None
        self.bind(None)

    def bind(self, car):
        self.unbind(car)
        self.car = car

    def unbind(self, car):
        self.remove_bullet_object()
        self.car = None
        
    def _update_spatial(self, coord):
        loc = self.car.location
        if loc is not None:
            lwh = self.car.lwh
            self.pos_road = loc.pos
            self.yaw_road = loc.yaw
            self.pos = coord.road_2d_to_spatial_3d_pt(self.pos_road)
            self.pos = np.add(self.pos, np.multiply(coord.height_3d(), lwh[2]*0.5))
            self.orient_aa = coord.road_2d_to_spatial_3d_yaw_aa(self.yaw_road)
            if self.has_bullet_object() == False:
                self.create_bullet_object(self.pos, self.orient_aa, lwh)
            else:
                self.teleport_bullet_object(self.pos, self.orient_aa)
        else:
            self.remove_spatial_object()
            
    def sg_update_matrix_self(self, coord):
        self._update_spatial(coord)
        self._matrix_s2p = umath.mat_transl_aa(self.pos, self.orient_aa)
        
    def sg_matrix_s2p(self):
        return self._matrix_s2p
