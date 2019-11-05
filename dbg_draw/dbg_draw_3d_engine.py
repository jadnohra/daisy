from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy
import math
import copy
import time
import os, sys
try:
	import fcntl
except ImportError:
	fcntl = None

from dbg_draw.dbg_draw_engine import *


def scene_viewport_init(w, h, aa = True):
	glClearColor(0.0, 0.0, 0.0, 0.0)
	glCullFace(GL_BACK)
	glClearDepth(1.0)
	glDepthFunc(GL_LESS)
	glEnable(GL_DEPTH_TEST)
	glShadeModel(GL_SMOOTH)
	glViewport(0, 0, w, h);
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(60.0, float(w)/float(h), 0.01, 1000.0)
	glMatrixMode(GL_MODELVIEW)
	glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )

	glEnable(GL_MULTISAMPLE)
	if (aa):
		glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable (GL_BLEND)
		glEnable (GL_LINE_SMOOTH)
		glHint (GL_LINE_SMOOTH_HINT, GL_NICEST)
		glEnable (GL_POLYGON_SMOOTH)
		glHint (GL_POLYGON_SMOOTH_HINT, GL_NICEST)

def scene_update_cam():
	ctx = g_scene_context; crds = ctx['cam_coords'];
	for k in ctx['cam_key_on']:
		if (ctx['cam_key_on'][k]):
			vec = ctx['cam_keys'][k]
			ci = [abs(x) for x in vec].index(1.0)
			vec = vec_muls(vec, ctx['cam_speeds'][ci])
			ctx['cam_coords'] = vec_add(ctx['cam_coords'], vec)
	ctx = g_scene_context; crds = ctx['cam_coords'];
	crds[2] = max(0.001, crds[2])
	crds[1] = min(math.pi/2.0-0.001, max(0.001, crds[1]))
	pt = coord_sph_to_cart(*crds);
	cz = vec_normd(pt); cx = v3_cross([0.0,0.0,1.0], cz);
	if (vec_norm(cx) <= 1.e-6):
		cx = v3_cross(mat_transp(ctx['CamM'])[1].tolist(), cz)
	cy = vec_normd(v3_cross(cz, cx)); cx = vec_normd(v3_cross(cy, cz));
	mat_set_transl(ctx['CamM'], pt); mat_set_rot(ctx['CamM'], mat_transp([ cx, cy, cz ]));
	g_scene_context['ViewM'] = mat_rigid_inv(g_scene_context['CamM'])

def scene_color_zero(r,g,b):
	glColor3f(0.0,0.0,0.0)

def scene_color_pass(r,g,b):
	glColor3f(r,g,b)

def scene_do_draw():
	ctx = g_scene_context
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	if arg_has('-fill'):
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
		glMatrixMode(GL_MODELVIEW)
		ctx['draw_func'](ctx, scene_color_pass)
	else:
		if (not arg_has('-fancy')):
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
			glMatrixMode(GL_MODELVIEW)
			ctx['draw_func'](ctx, scene_color_pass)
		else:
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
			glMatrixMode(GL_MODELVIEW)
			glColor3f(0.0,0.0,0.0)
			ctx['draw_func'](ctx, scene_color_zero)

			glEnable(GL_POLYGON_OFFSET_LINE);
			glPolygonOffset(-1,-1);

			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
			glMatrixMode(GL_MODELVIEW)
			ctx['draw_func'](ctx, scene_color_pass)

			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
			glDisable(GL_POLYGON_OFFSET_LINE);

	glutSwapBuffers()


def scene_xfm(M):
	glLoadMatrixf(mat_transp(mat_mul(g_scene_context['ViewM'], M)))

def scene_xfm_id():
	glLoadMatrixf(mat_transp(g_scene_context['ViewM']))

def scene_draw_cs(basis, col_func):
	idb = [(1.0,0,0), (0,1.0,0), (0,0,1.0)]
	for b,ax in zip(basis, idb):
		scene_draw_line(v3_z(), [b*x for x in ax], ax, col_func)

def scene_draw_line(v1, v2, col, col_func):
	col_func(*col); glBegin(GL_LINES); glVertex3f(*v1); glVertex3f(*v2); glEnd();

def scene_draw_vline(verts, indices, col, col_func):
	col_func(*col); glBegin(GL_LINE_STRIP);
	for i in indices:
		glVertex3f(*verts[i])
	glEnd();

def scene_draw_vface(verts, indices, col, col_func):
	col_func(*col); glBegin(GL_LINE_STRIP);
	for i in indices + [indices[0]]:
		glVertex3f(*verts[i])
	glEnd();

def scene_draw_box(dim=[1.0,1.0,1.0]):
	dim = [0.5*x for x in dim]
	glBegin(GL_QUADS)
	glVertex3f(dim[0], dim[1],-dim[2]); glVertex3f(-dim[0], dim[1],-dim[2]); glVertex3f(-dim[0], dim[1], dim[2]); glVertex3f(dim[0], dim[1], dim[2]);
	glVertex3f(dim[0],-dim[1], dim[2]); glVertex3f(-dim[0],-dim[1], dim[2]); glVertex3f(-dim[0],-dim[1],-dim[2]); glVertex3f(dim[0],-dim[1],-dim[2]);
	glVertex3f(dim[0], dim[1], dim[2]); glVertex3f(-dim[0], dim[1], dim[2]); glVertex3f(-dim[0],-dim[1], dim[2]); glVertex3f(dim[0],-dim[1], dim[2]);
	glVertex3f(dim[0],-dim[1],-dim[2]); glVertex3f(-dim[0],-dim[1],-dim[2]); glVertex3f(-dim[0], dim[1],-dim[2]); glVertex3f(dim[0], dim[1],-dim[2]);
	glVertex3f(-dim[0], dim[1], dim[2]); glVertex3f(-dim[0], dim[1],-dim[2]); glVertex3f(-dim[0],-dim[1],-dim[2]); glVertex3f(-dim[0],-dim[1], dim[2]);
	glVertex3f(dim[0], dim[1],-dim[2]); glVertex3f(dim[0], dim[1], dim[2]); glVertex3f(dim[0],-dim[1], dim[2]); glVertex3f(dim[0],-dim[1],-dim[2]);
	glEnd()

def scene_draw_point(dim=1.0):
	glPointSize(dim)
	glBegin(GL_POINTS)
	glVertex3f(*v3_z());
	glEnd();

def scene_draw_point_pos(pos, dim=1.0):
	glPointSize(dim)
	glBegin(GL_POINTS)
	glVertex3f(pos[0], pos[1], pos[2])
	glEnd();
	
def scene_draw_points_pos(points_pos, dim=1.0):
	glPointSize(dim)
	glBegin(GL_POINTS)
	for pos in points_pos:
		glVertex3f(pos[0], pos[1], pos[2])
	glEnd();	

def scene_draw_lines(pt_pairs):
	glBegin(GL_LINES); 
	for v1, v2 in pt_pairs:
		glVertex3f(*v1) 
		glVertex3f(*v2)
	glEnd();


def scene_test_draw(sctx, col_func):
	t = sctx['t']

	glLoadMatrixf(mat_transp(mat_transl_aa((0.0,0.0,-18.0), [1.0,1.0,0.0,t])))
	col_func(1.0,1.0,1.0)
	scene_draw_box([2.0,1.0,0.5])

	glLoadMatrixf(mat_transp(mat_transl_aa((-3.0,0.0,-12.0), [1.0,0.0,1.0,t*0.5])))
	col_func(0.0,0.0,1.0)
	scene_draw_box()

def scene_3d_go(scene_title, scene_update, scene_draw):
	funcs = {'viewport_init':scene_viewport_init, 'update_cam':scene_update_cam, 'do_draw': scene_do_draw }
	scene_go(scene_title, scene_update, scene_draw, funcs)
