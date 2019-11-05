import numpy as np
import math


def m_sq(a):
    return a*a
def m_sqrt(a):
    return np.sqrt(a)
def m_sgn(a):
    return 1 if a>=0.0 else -1
def mat_set_transl(M, vec):
    M[:3, 3] = vec[:3]
def mat_get_transl(M):
    return M[:3, 3]
def mat_add_transl(M, vec):
    mat_set_transl(M, vec_add(mat_get_transl(M), vec))
def v3_z():
    return [0.0]*3
def v2_z():
    return [0.0]*2
def vec_norm(v):
    return np.linalg.norm(v)
def vec_normd(v):
    n = vec_norm(v); return v / n if n != 0.0 else v;
def vec_neg(v):
    return [-x for x in v]
def vec_muls(v, s):
    return [x*s for x in v]
def vec_mul(v1, v2):
    return [x1*x2 for x1,x2 in zip(v1, v2)]
def vec_add(v1, v2):
    return [x1+x2 for x1,x2 in zip(v1, v2)]
def vec_dot(v1, v2):
    return np.dot(v1, v2)
def v3_cross(v1, v2):
    return np.cross(v1, v2)
def vec_sub(v1, v2):
    return [x1-x2 for x1,x2 in zip(v1, v2)]
def uquat_id():
    return [1.0] + v3_z()
def quat_mul(q1, q2):
    w0, x0, y0, z0 = q2; w1, x1, y1, z1 = q1;
    return np.array([-x1*x0 - y1*y0 - z1*z0 + w1*w0,
                         x1*w0 + y1*z0 - z1*y0 + w1*x0,
                        -x1*z0 + y1*w0 + z1*x0 + w1*y0,
                         x1*y0 - y1*x0 + z1*w0 + w1*z0])
def uquat_to_mat(q):
    q = np.array(q)
    n = np.dot(q, q)
    if n == 0.0:
        return mat_id()
    q *= math.sqrt(2.0 / n)
    q = np.outer(q, q)
    return np.array([
        [1.0-q[2, 2]-q[3, 3],     q[1, 2]-q[3, 0],     q[1, 3]+q[2, 0]],
        [    q[1, 2]+q[3, 0], 1.0-q[1, 1]-q[3, 3],     q[2, 3]-q[1, 0]],
        [    q[1, 3]-q[2, 0],     q[2, 3]+q[1, 0], 1.0-q[1, 1]-q[2, 2]]
        ])
def rv_to_uquat(rv):
    a = vec_norm(rv)/2.0; return [math.cos(a)] + vec_muls(vec_normd(rv), math.sin(a))
def aa_to_mat(aa): # http://www.lfd.uci.edu/~gohlke/code/transformations.py.html
    sina = math.sin(aa[3]); cosa = math.cos(aa[3]); axis = vec_normd(aa[:3])
    R = np.diag([cosa, cosa, cosa]); R += np.outer(axis, axis) * (1.0 - cosa);
    vec = np.array(axis) * sina
    R += np.array([[ 0.0,-vec[2],  vec[1]], [ vec[2], 0.0, -vec[0]], [-vec[1], vec[0],  0.0]])
    return R
def rv_to_mat(rv):
    return uquat_to_mat(rv_to_uquat(rv))
def mat_to_aa(R):
    axis = np.zeros(3, np.float64)
    axis[0] = R[2,1] - R[1,2]; axis[1] = R[0,2] - R[2,0]; axis[2] = R[1,0] - R[0,1];
    r = np.hypot(axis[0], np.hypot(axis[1], axis[2]))
    t = R[0,0] + R[1,1] + R[2,2]
    angle = math.atan2(r, t-1)
    axis = axis / r
    return axis.tolist() + [angle]
def mat_to_rv(R):
    aa = mat_to_aa(R); return np.multiply(aa[:3], aa[3])[:3];
def mat_set_rot(M, R):
    M[:3, :3] = R
def mat_set_scl(M, S):
    for i in range(3):
        M[i, i] = S[i]
def mat_id():
    return np.identity(4)
def mat3_to_mat4(R):
    M = mat_id(); mat_set_rot(M, R); return M;
def mat_transl_aa(transl, aa):
    M = mat_id(); R = aa_to_mat(aa); mat_set_rot(M, R);
    mat_set_transl(M, transl)
    return M
def mat_transl_R(transl, R):
    M = mat_id(); mat_set_rot(M, R); mat_set_transl(M, transl); return M;
def mat_transl(transl):
    M = mat_id(); mat_set_transl(M, transl); return M;
def mat_transp(M):
    return np.transpose(M)
def mat_rigid_inv(M):
    return np.linalg.inv(M)
def mat_inv(M):
    return np.linalg.inv(M)
def mat4_mul_pt(M, pt):
    return np.dot(M, [x for x in pt]+[1.0])[:3]
def mat4_mul_vec(M, vec):
    return np.dot(M, [x for x in vec]+[0.0])[:3]
def mat_mul_vec(M, vec):
    return np.dot(M, vec)
def mat_mul(M1, M2):
    return np.dot(M1, M2)
def mat_mul_diag(M, D):
    return np.multiply(M,D)

def rand_between(a, b):
    return a+(np.random.rand() * (b-a))
def rand_ampl(ampl):
    return 2.0*(np.random.rand()-0.5) * ampl
def rand_sgn():
    return m_sgn(rand_ampl(1.0))
def rand_ind(ln):
    return int(np.clip(round(np.random.rand()*float(ln)), 0, ln-1))

def vec_prec_str(v, prec):
    if (prec <= 0) or (prec is None):
        return v
    fmt = '{{:.{}g}}'.format(prec); return ','.join([fmt.format(x) for x in v]);
def vec_prec(v, prec):
    return [float(x) for x in vec_prec_str(v, prec).split(',')]

def rand_ampl_prec(ampl, prec=2):
    return vec_prec([rand_ampl(ampl)], prec)[0]

def coord_sph_to_cart(az, pol, rad):
    rcos_theta = rad * math.cos(pol)
    z = rad * math.sin(pol)
    x = rcos_theta * math.cos(az)
    y = rcos_theta * math.sin(az)
    return (x,y,z)

def rad_deg(a):
    return (a/(math.pi))*180.0
def deg_rad(a):
    return (a/(180.0))*math.pi
def rad_0_x(a, x):
    return a - math.floor(a/(x))*(x)
def rad_0_2pi(a):
    return rad_0_x(a, 2.0*math.pi)
def rad_0_pi(a):
    return rad_0_x(a, math.pi)
def rad_0_pi2(a):
    return rad_0_x(a, math.pi/2.0)
def rad_deg(a):
    return (a/(math.pi))*180.0
def deg_rad(a):
    return (a/(180.0))*math.pi
def v2_dist(a,b):
    v = [b[0]-a[0], b[1]-a[1]]; return math.sqrt(v[0]*v[0]+v[1]*v[1]);

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Lines given as (point, dir) pairs
# Output is parametric factors for each line: (t0, t1)
def intersect_two_lines(line0, line1): 
    d0, d1 = line0[1], line1[1]
    p0, p1 = line0[0], line1[0]
    a = np.array([[d0[0], -d1[0]], [d0[1], -d1[1]]])
    b = np.subtract(p1, p0)
    return np.linalg.solve(a, b)