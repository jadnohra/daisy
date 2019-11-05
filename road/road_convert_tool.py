import sys
import os
import road
import road_convert


road_file = (sys.argv[sys.argv.index('--file')+1]
             if '--file' in sys.argv else None)
out_file = (sys.argv[sys.argv.index('--out')+1]
            if '--out' in sys.argv else None)
format = (sys.argv[sys.argv.index('--format')+1]
          if '--format' in sys.argv else None)
format = os.path.splitext(out_file)[1] if out_file else format

rd = road.Road()
rd.load_file(road_file)
if format == 'svg':
    road_convert.write_road_svg(rd, road_file + '.svg')
else:
    arg_center = '--no_center' not in sys.argv
    arg_yup = '--z_up' not in sys.argv
    unproj = road_convert.CurveUnproj3D()
    arg_lane_width = (int(sys.argv[sys.argv.index('--lane_width')+1])
                      if '--lane_width' in sys.argv else 10.0)
    road_convert.write_road_obj(rd, road_file + '.obj',
                                unproj, arg_center, arg_yup)
    road_convert.write_road_obj_mesh(rd, road_file + '.mesh.obj',
                                     arg_lane_width,
                                     unproj, arg_center, arg_yup)
