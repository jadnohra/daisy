
'''
Road: The road 2d world coordinate system is a 2D euclidean coordinate system. 
The intended semantics are 
    - the x axis is identified with (1,0) and considered to be pointing right
    - the y axis is identified with (0,1) and considered to be pointing up
    
                                    y
                                    ^
                                    |
                                    |-----> x
    - The units are intended to be in meters
    
Spatial: The spatial 3D wold coordinate system is a right-handed 3D euclidean coordinate system. 
The intended semantics are the OpenGL conventions:
    - the x axis is identified with (1,0,0) and considered to be pointing right
    - the y axis is identified with (0,1,0) and considered to be pointing up
    - the z axis is identified with (0,1,0) and considered to be pointing back
    
                                    y
                                    ^
                                    |
                                    |-----> x
                                   /
                                  /
                                z 
    
We also use the OpenGL conventional projection matrices. The 3D world is projected into a 2D screen space where
    - the x axis is identified with (1,0) and considered to be pointing right. 
    It is the projection of the 3D x axis.
    - the y axis is identified with (0,1) and considered to be pointing up. It is the projection of the 3D y axis.
    - Implicitly, the 3D z axis points from the screen to the watcher
    
                                    y
                                    ^
                                    |
                                    |-----> x

The coordinate systems are designed such that the semantics of the road coordinate systems 
are preserved when transformed through the spatial 3D world and rendered into screen space.

The road plane is embedded into the spatial 3D world by translating (sliding) the 3D xy plane arbitrarily. 
Hence, the transformation between the two coordinate systems requires a sliding 3D vector that translates 
the origin of the 3D xy plane into the origin of the road in the embedded plane.
Since the sliding only involves a translation, vectors and angles can be transformed without 
using the sliding vector.

TODO: find the IEEE standard    
'''

'''
    - pry stands for (pitch, roll, yaw)
    - aa stands for an axis-angle rotation
    - rvec stands for a rotation vector 
'''
class CoordXfm:
    def __init__(self, sliding):
        self.sliding = sliding

    def height_3d(self):
        return [0.0, 0.0, 1.0]
        
    def offset_height_3d(self, vec, offset):
        h = self.height_3d()
        return [vec[0]+h[0]*offset, vec[1]+h[1]*offset, vec[2]+h[2]*offset]
        
    def road_2d_to_spatial_3d_yaw_pry(self, yaw):
        return [0.0, 0.0, yaw]

    def road_2d_to_spatial_3d_yaw_aa(self, yaw):
        return self.height_3d() + [yaw]
        
    def road_2d_to_spatial_3d_yaw_rvec(self, yaw):
        aa = self.road_2d_to_spatial_3d_yaw_aa(yaw)
        return [x*aa[3] for x in aa[:3]]

    def world_3d_to_spatial_2d_pry_yaw(self, pry):
        return pry[2]

    def world_3d_to_spatial_2d_aa_yaw(self, aa):
        # TODO
        return None

    def road_2d_to_spatial_3d_vec(self, p):
        return [p[0], p[1], 0.0]
        
    def world_3d_to_spatial_2d_vec(self, pt):
        return [p[0], p[1]]

    def road_2d_to_spatial_3d_pt(self, p):
        return [p[0]-self.sliding[0], p[1]-self.sliding[1], -self.sliding[2]]
        
    def world_3d_to_spatial_2d_pt(self, p):
        return [p[0]+self.sliding[0], p[1]+self.sliding[1]]