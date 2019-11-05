from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import platform
import numpy
import math
import copy
import time
import os, sys
from util.math import *
from util.arg import *

try:
	import fcntl
except ImportError:
	fcntl = None


col_wt = [1.0,1.0,1.0]
col_rd = [1.0,0.0,0.0]
col_grn = [0.0,1.0,0.0]
col_bl = [0.0,0.0,1.0]
col_blk = [0.0,0.0,0.0]
col_ylw = [1.0, 1.0, 0.0]

def hsv2rgb(h, s, v):
	hi = int(h*6)
	f = h*6 - hi
	p = v * (1 - s); q = v * (1 - f * s); t = v * (1 - (1 - f) * s);
	r, g, b = 0, 0, 0
	if hi == 0: r, g, b = v, t, p
	elif hi == 1: r, g, b = q, v, p
	elif hi == 2: r, g, b = p, v, t
	elif hi == 3: r, g, b = p, q, v
	elif hi == 4: r, g, b = t, p, v
	elif hi == 5: r, g, b = v, p, q
	return [r, g, b]

g_randcol_h = 0.0
def randcol():
	global g_randcol_h
	golden_ratio_conjugate = 0.618033988749895
	g_randcol_h = g_randcol_h + golden_ratio_conjugate
	g_randcol_h = g_randcol_h % 1.0
	return hsv2rgb(g_randcol_h, 0.5, 0.95)

def obj_init_color(obj):
	if arg_has('-mono'):
		obj['col'] = col_wt
	else:
		obj['col'] = randcol()

def scene_empty_update(sctx):
	return True

def scene_empty_draw(sctx, col_func):
	return

g_scene_context = {
	'wind_handle' : 0,
	'wind_w' : 640,
	'wind_h' : 480,
	'wind_vis' : None,
	'update_func' : scene_empty_update,
	'draw_func' : scene_empty_draw,
	'stop_frame': int(arg_get('-stop_frame', -1)),
	'frame' : 0, 't' : 0.0, 'dt' : 0.0, 'last_clock_mt' : 0,
	'fixed_dt' : 0, 'adapt_fixed_dt': True,
	'paused' : False, 'paused_step' : False,
	'loop_frame' : 0,
	'fps_last_clock_mt': 0, 'fps_marker' : 0, 'fps' : 0,
	'scene': {},
	'update_print': '',
	'ViewM': mat_id(), 'CamM': mat_id(),
	'cam_coords': [-math.pi/2, math.pi/4, 150.0], 'cam_def_coords': [-math.pi/2, math.pi/4, 150.0], 'cam_speeds':[0.06, 0.06, 0.6],
	'cam_keys': {'w':[0.0,0.0,-1.0], 's':[0.0,0.0,1.0], 'a':[-1.0,0.0,0.0], 'd':[1.0,0.0,0.0], 'q':[0.0,-1.0,0.0], 'e':[0.0,1.0,0.0]},
	'cam_key_on': {},
	'funcs': {'viewport_init':None, 'update_cam':None, 'do_draw': None }
	}

def scene_exit():
	if arg_has(['-live_print']):
		print ('\n')
	if bool(glutLeaveMainLoop):
		glutLeaveMainLoop()
	else:
		sys.exit(0)

def scene_def_input(bkey, x, y):
	bkey = bkey.decode("utf-8") # seems to be needed for python-3
	ctx = g_scene_context
	if bkey == '\033':
		scene_exit()
	elif bkey == '\r':
		ctx['paused'] = not ctx['paused']
	elif bkey == ' ':
		ctx['paused_step'] = True
	elif (bkey in ctx['cam_keys']):
		ctx['cam_key_on'][bkey] = True
	elif (bkey == 'r'):
		ctx['cam_coords'][:] = ctx['cam_def_coords'][:]
	#else:
	#    print(bkey)

def scene_def_up_input(bkey, x, y):
	bkey = bkey.decode("utf-8") # seems to be needed for python-3
	ctx = g_scene_context
	if (bkey in ctx['cam_keys']):
		ctx['cam_key_on'][bkey] = False

def scene_visibility_func(state):
	g_scene_context['wind_vis'] = state

def scene_idle_func():
	if (g_scene_context['wind_vis'] == GLUT_VISIBLE):
		scene_loop_func()
	return


def handle_console_input():
	if True: # seems broken with python3
		return
	if fcntl is not None:
		ctx = g_scene_context
		if (ctx['loop_frame'] == 0):
			fd = sys.stdin.fileno()
			fl = fcntl.fcntl(fd, fcntl.F_GETFL)
			fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
		try:
			input = sys.stdin.readline()
			print ('echo:', input,)
		except:
			return

def wnd_reshape(w, h):
	ctx = g_scene_context
	ctx['wind_w'] = w
	ctx['wind_h'] = h
	if (ctx['funcs']['viewport_init']):
		ctx['funcs']['viewport_init'](w, h)

def update_live_print(ctx, clock_mt):
	if arg_has(['-live_print']) or len(ctx['update_print']):
		if (ctx['loop_frame'] > 0):
			sys.stdout.write('\x1B[2K')

		print_strs = []
		if arg_has(['-live_print']):
			if (clock_mt - ctx['fps_last_clock_mt'] >= 1000):
				ctx['fps'] = (ctx['loop_frame'] - ctx['fps_marker']) / ((clock_mt - ctx['fps_last_clock_mt'])/1000.0)
				ctx['fps_last_clock_mt'] = clock_mt; ctx['fps_marker'] = ctx['loop_frame'];
			print_strs.append('frame: {}, time: {:.3f}, fps: {:.2f}'.format(ctx['frame'], ctx['t'], ctx['fps']))
		if len(ctx['update_print']):
			print_strs.append(ctx['update_print'])
		sys.stdout.write('\r{}'.format(' '.join(['[{}]'.format(x) for x in print_strs]) ))
		sys.stdout.flush()

def scene_loop_func():
	handle_console_input()
	try:
		print_arg_help()
		ctx = g_scene_context
		ctx['funcs']['update_cam']()
		if (ctx['loop_frame'] == 0):
			ctx['last_clock_mt'] = glutGet(GLUT_ELAPSED_TIME)
		clock_mt = glutGet(GLUT_ELAPSED_TIME)
		mdt = clock_mt - ctx['last_clock_mt']
		if (mdt > 0):

			ctx['last_clock_mt'] = clock_mt

			do_draw = True; do_frame = False;
			if (ctx['paused'] == False) or (ctx['paused_step'] == True):
				if (ctx['fixed_dt'] != 0):
					dt_count = 1
					if (ctx['adapt_fixed_dt'] and (not ctx['paused_step'])):
						dt_count =  max(1, min(8, int(math.ceil((mdt/1000.0) / ctx['fixed_dt']))))
					for i in range(dt_count):
						ctx['dt'] = ctx['fixed_dt']
						do_frame = ctx['update_func'](ctx)
						if (do_frame):
							ctx['t'] = ctx['t'] + ctx['fixed_dt']
				else:
					ctx['dt'] = mdt/1000.0;
					do_frame = ctx['update_func'](ctx)
					if (do_frame):
						ctx['t'] = ctx['t'] + mdt/1000.0;
			else:
				if (ctx['frame'] == 0):
					do_draw = False
			ctx['paused_step'] = False

			update_live_print(ctx, clock_mt)

			if (do_draw):
				ctx['funcs']['do_draw']()

			if (do_frame):
				if ctx['stop_frame'] != -1 and ctx['frame'] == ctx['stop_frame']:
					scene_exit()
				ctx['frame'] = ctx['frame']+1

		ctx['loop_frame'] = ctx['loop_frame']+1
	except:
		traceback.print_exc()
		sys.exit()


#http://stackoverflow.com/questions/1892339/how-to-make-a-window-jump-to-the-front
import subprocess
def pyogl_mac_focus_hack():
	def applescript(script):
		return subprocess.check_output(['/usr/bin/osascript', '-e', script])
	applescript('''
		tell app "System Events"
			repeat with proc in every process whose name is "Python"
				set frontmost of proc to true
				exit repeat
			end repeat
		end tell''')

def scene_go(title, update_func, draw_func,
						mode_funcs, input_func = scene_def_input):
	global g_scene_context

	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | (GLUT_MULTISAMPLE if not arg_has('-no_multisample') else 0) ) #
	glutInitWindowSize(g_scene_context['wind_w'], g_scene_context['wind_h'])
	glutInitWindowPosition(200,200)

	g_scene_context['funcs'] = mode_funcs
	g_scene_context['wind_handle'] = glutCreateWindow(title)
	g_scene_context['update_func'] = update_func
	g_scene_context['draw_func'] = draw_func
	g_scene_context['paused'] = arg_has('-paused')
	if (not arg_has_key('-flex_dt')):
		fixed_dt = float(eval(arg_get('-dt', '1.0/60.0')))
		if (fixed_dt <= 0):
			fixed_dt = float(eval(arg_get('-dt','')+'.0'))
		if (fixed_dt <= 0):
			sys.exit()
		g_scene_context['fixed_dt'] = fixed_dt
		g_scene_context['adapt_fixed_dt'] = arg_has('-adapt_fixed_dt')

	glutReshapeFunc(wnd_reshape)
	glutDisplayFunc(scene_loop_func)
	glutIdleFunc(scene_idle_func)
	glutVisibilityFunc(scene_visibility_func)
	glutKeyboardFunc(input_func)
	glutKeyboardUpFunc(scene_def_up_input)
	g_scene_context['funcs']['viewport_init'](g_scene_context['wind_w'], g_scene_context['wind_h'])
	if platform.system() == 'Darwin':
		pyogl_mac_focus_hack()
	glutMainLoop()
