import pybullet as bullet
import numpy as np
import sys

class SpatialEngine:
    def __init__(self, entities, coord):
        bullet.connect(bullet.GUI if '-bullet_gui' in sys.argv else bullet.DIRECT)
        self.ground_coll_shape = None
        self.ground_plane_bid = None
        self.entities = entities
        self.coord = coord
        self._box_distance_cache = {}
        self._collision_cache = {}
        
    def add_ground_plane(self, size):
        if self.ground_plane_bid is not None:
            bullet.removeBody(self.ground_plane_bid)
            bullet.removeCollisionShape(self.ground_coll_shape)
        size_height = 1.0
        pos = [0,0,0]
        pos = np.add(pos, np.multiply(self.coord.height_3d(), -size_height*0.5))
        coll_shape = bullet.createCollisionShape(bullet.GEOM_BOX, halfExtents=[0.5*x for x in [size, size, size_height]])
        bid = bullet.createMultiBody(baseMass=0,
                                    baseCollisionShapeIndex=coll_shape,
                                    basePosition=pos)
        self.ground_coll_shape = coll_shape
        self.ground_plane_bid = bid
        
    def get_box_distance(self, entity_1, entity_2):
        bid_pair = (entity_1.spatial.bid, entity_2.spatial.bid)
        cached_dist = self._box_distance_cache.get(bid_pair, None)
        if cached_dist is not None:
            return cached_dist
        closest_pts = bullet.getClosestPoints(entity_1.spatial.bid, entity_2.spatial.bid, float('inf'))
        closest_dists = [info[8] for info in closest_pts]
        closest_dist = np.amin(closest_dists)
        self._box_distance_cache[bid_pair] = closest_dist
        self._box_distance_cache[tuple(reversed(bid_pair))] = closest_dist
        return closest_dist
        
        
    def detect_collision(self, entity_1, entity_2):
        #bid_pair = (entity_1.spatial.bid, entity_2.spatial.bid)
        #cached_coll = self._collision_cache.get(bid_pair, None)
        #if cached_coll is not None:
        #    return cached_coll
        contact_pts = bullet.getContactPoints(entity_1.spatial.bid, entity_2.spatial.bid)
        has_coll = len(contact_pts) > 0
        #self._collision_cache[bid_pair] = has_coll
        #self._collision_cache[tuple(reversed(bid_pair))] = has_coll
        return has_coll
    
    def get_entities_in_radius(self, entity, radius, entities):
        # TODO optimize
        dist_ents = []
        for ent in entities:
            if entity.id != ent.id and ent.has_component('spatial') and ent.spatial.has_bullet_object():
                dist = self.get_box_distance(entity, ent)
                if dist <= radius:
                    dist_ents.append([ent, dist])
        return dist_ents
    
    def get_entities_in_fov(self, entity, radius, fov, entities):
        # TODO optimize
        entity_pos = entity.spatial.pos_road
        entity_yaw = entity.spatial.yaw_road
        fov_ents = []
        for ent in entities:
            if (entity.id != ent.id and ent.has_component('spatial') and ent.spatial.has_bullet_object()):
                    dist = self.get_box_distance(entity, ent)
                    if dist <= radius:
                        vec = np.subtract(ent.spatial.pos_road, entity_pos)
                        yaw_dir = np.arctan2(vec[1], vec[0])
                        x, y = entity_yaw, yaw_dir
                        dyaw = np.arctan2(np.sin(x-y), np.cos(x-y))
                        if np.abs(dyaw) <= 0.5*fov:
                            fov_ents.append([ent, dist, dyaw])
        return fov_ents

    def cast_rays_spherical(self, origin, azimuth_from, azimuth_to, azimuth_res,
                            polar_from, polar_to, polar_res, max_ray_len):
        
        def interp(frm, to, i, res):
            return frm + (to - frm) * (i / float(max(res-1, 1)))
        
        ray_count = polar_res*azimuth_res
        to_pts = [None]*ray_count
                
        ray_i = 0
        for pol_i in range(polar_res):
            el = interp(polar_from, polar_to, pol_i, polar_res)
            rcos_theta = max_ray_len * np.cos(el)
            z = max_ray_len * np.sin(el)
            for azi_i in range(azimuth_res):
                az = interp(azimuth_from, azimuth_to, azi_i, azimuth_res)
                x = rcos_theta * np.cos(az)
                y = rcos_theta * np.sin(az)
                to_pts[ray_i] = (x,y,z)
                ray_i = ray_i + 1

        results = []
        tested_ray_count = 0
        while ray_count-tested_ray_count > 0:
            # the '-1' is due to seemingly a bug in pybullet, which seems to return 
            # one result less than the batch size, when using the full batch size
            batch_size = min(ray_count-tested_ray_count, bullet.MAX_RAY_INTERSECTION_BATCH_SIZE-1)  
            batch_results = bullet.rayTestBatch([origin]*batch_size, to_pts[tested_ray_count: tested_ray_count+batch_size])
            results.extend(batch_results)
            tested_ray_count = tested_ray_count + batch_size
        hits = [None]*ray_count
        hit_i = 0
        for i in range(ray_count):
          hit_uid = results[i][0]
          if hit_uid >= 0:
            hit_pos = results[i][3]
            hits[hit_i] = (hit_uid, hit_pos)
            hit_i = hit_i + 1
        
        return hits[:hit_i]
        
    def update_entity_sg(self, comp):
        # A simple unconditional depth-first traversal will do for now
        # TODO optimize if scene-graphs become large
        def recurse_update_sg(node, parent):
            node.sg_update_matrix_self(self.coord)
            node.sg_update_matrix_world(parent)
            for child in node.sg_children():
                recurse_update_sg(child, node)
        recurse_update_sg(comp, None)
    
    def step(self, t, dt):
        self._box_distance_cache = {}
        self._collision_cache = {}
        bullet.stepSimulation()
        for entity in self.entities:
            comp = entity.get_component('spatial')
            if comp is not None:
                self.update_entity_sg(comp)