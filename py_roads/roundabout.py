from pyroad import *
import util.math as um

class Road(PyRoad):

    def get_description(self):
        return 'A roundabout'

    def get_asciiart(self):
        return \
    '''
                    |
                    i_in
                    |
                /---i---\\
              i+1        \\
   --i+1_in---/           \\
            ...           ...
    '''

    def get_param_descriptions(self):
        return {'r':'Radius (default: 20)',
                'n':'Number of branches (default: 5)',
                'a':'Rotation angle (default: 0)',
                }

    def build(self, b, params):
        def angle_to_vert(angle, rad):
            x,y,z = um.coord_sph_to_cart(um.deg_rad(angle), 0.0, rad)
            return x,y
        n = int(params.get('n', 9))
        rad = float(params.get('r', 20.0))
        a0 = float(params.get('a', 0.0))
        da = 360.0 / n
        
        # TODO arcs: need a new feature preserve_normals instead of tangents
        # TODO lanes
        
        verts = []
        angles = []
        for i in range(n):
            angle = a0 + da * i
            angles.append(angle)
            verts.append(angle_to_vert(angle, rad))
        
        for i in range(n):
            ia = i
            ib = (i+1) % n
            b.curve(str(i)).start_at(verts[ia]).end_at(verts[ib])
            b.link(str(ia), str(ib))
            b.curve(str(i)+'_in').end_at(verts[ia]).angle(angles[ia]+180).length(rad)
            b.link(str(i)+'_in', str(ia))