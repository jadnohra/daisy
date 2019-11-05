import numpy as np

try:
    import svgwrite
except ImportError:
    svgwrite = None

try:
    import pyclipper
except ImportError:
    pyclipper = None


def write_curve_svg(curve, dwg):
    def vertex_to_svg(vert):
        return tuple([vert[x]*svgwrite.cm for x in [0, 1]])
    rgb_255 = [int(x*255.0) for x in curve.rgb]
    dwg.add(dwg.line(vertex_to_svg(curve.world_start),
                     vertex_to_svg(curve.world_end),
                     stroke=svgwrite.rgb(
                     rgb_255[0], rgb_255[1], rgb_255[2], '%'),
                     stroke_width=3
                     ))


def curve_segments_to_vert_pair_list(verts, lines):
    vert_pair_list = []
    for seg in lines:
        for i in range(len(seg)-1):
            vert_pair_list.append([verts[seg[i]], verts[seg[i+1]]])
    return vert_pair_list


class CurveUnproj3D:
    def __init__(self):
        self.z = 0.0
        self.delta_length = 10.0

def calc_curve_segments(curve, verts, lines, dl=None, vert_func=None):
    vert_func = (lambda x: x) if vert_func is None else vert_func
    dl = min(10.0, curve.get_length() / 3.0) if dl is None else dl
    if curve.is_curved():
        sampled_ts = curve.sample_t(dl)
        part_verts = [vert_func(curve.t_to_point(t)) for t in sampled_ts]
        base_vi = len(verts)
        part_line = range(base_vi, base_vi+len(part_verts))
        verts.extend(part_verts)
        lines.append(part_line)
    else:
        vi = len(verts)
        verts.append(vert_func(curve.t_to_point(0)))
        verts.append(vert_func(curve.t_to_point(1)))
        lines.append([vi, vi+1])

def calc_curve_obj(curve, unproj, verts, lines):
    def unproj_vert(vert_2d):
        return [vert_2d[0], vert_2d[1], unproj.z]
    dl = min(unproj.delta_length, curve.get_length() / 3.0)
    calc_curve_segments(curve, verts, lines, dl=dl, vert_func=unproj_vert)

def calc_rough_bounds(road):
    if len(road.curves) == 0:
        return ([0.0, 0.0], [0.0, 0.0])
    curve_0 = road.curves[0]
    bbox_min = [curve_0.world_start[0], curve_0.world_start[1]]
    bbox_max = [curve_0.world_start[0], curve_0.world_start[1]]
    for curve in road.curves:
        bbox_min = [min(curve.world_start[x], bbox_min[x])
                    for x in [0, 1]]
        bbox_min = [min(curve.world_end[x], bbox_min[x])
                    for x in [0, 1]]
        bbox_max = [max(curve.world_start[x], bbox_max[x])
                    for x in [0, 1]]
        bbox_max = [max(curve.world_end[x], bbox_max[x])
                    for x in [0, 1]]
    return (bbox_min, bbox_max)


def write_road_svg(road, svg_file):
    dwg = svgwrite.Drawing(svg_file, profile='tiny')
    for curve in road.curves:
        write_curve_svg(curve, dwg)
    dwg.save()


def calc_road_obj_polylines(road, unproj=CurveUnproj3D(), center=True):
    verts = []
    lines = []
    offset = [0.0, 0.0, 0.0]
    if center:
        bounds = calc_rough_bounds(road)
        offset_2d = [-0.5 * (bounds[0][x] + bounds[1][x]) for x in [0, 1]]
        offset = [offset_2d[0], offset_2d[1], 0.0]
    for curve in road.curves:
        calc_curve_obj(curve, unproj, verts, lines)
    offset_verts = [[x[i] + offset[i] for i in range(3)] for x in verts]
    return (offset_verts, lines, offset)


def obj_conv_yup(verts):
    return [[x[0], x[2], x[1]] for x in verts]


def write_obj_polylines(obj_file, verts, lines):
    with open(obj_file, 'w') as fout:
        for v in verts:
            fout.write('v {} {} {}\n'.format(v[0], v[1], v[2]))
        for l in lines:
            fout.write('l')
            for vi in l:
                fout.write(' {}'.format(vi+1))
            fout.write('\n')


def write_obj_faces(obj_file, verts, faces):
    with open(obj_file, 'w') as fout:
        for v in verts:
            fout.write('v {} {} {}\n'.format(v[0], v[1], v[2]))
        for f in faces:
            fout.write('f')
            for vi in f:
                fout.write(' {}'.format(vi+1))
            fout.write('\n')


def expand_centerlines(verts, lines, lane_width, func_collect):
    '''
             line
             .
             .
      <------. (vleft)
      1----3(v)-----5
      |      |      |
      |      |      |
      |      |      |
      0----2(pv)----4
      <------. (pvleft)
             .
    '''
    hw = lane_width / 2.0
    for li, l in enumerate(lines):
        for i, vi in enumerate(l[1:]):
            v = verts[vi]
            pv = verts[l[i]]
            ldir = np.cross([0.0, 0.0, 1.0], np.subtract(v, pv))
            vleft = ldir * (hw / np.linalg.norm(ldir))
            if i > 0:
                ppv = verts[l[i-1]]
                pldir = np.cross([0.0, 0.0, 1.0], np.subtract(pv, ppv))
                pvleft = pldir * (hw / np.linalg.norm(pldir))
            else:
                pldir = ldir
                pvleft = vleft
            part_verts = [
              np.add(pv, pvleft), np.add(v, vleft),
              pv, v,
              np.subtract(pv, pvleft), np.subtract(v, vleft)
              ]
            func_collect(li, part_verts)


def centerlines_to_mesh_simple(verts, lines, lane_width):
    '''
             line
             .
             .
      <------. (vleft)
      1----3(v)-----5
      |\     |\     |
      |  \   |  \   |
      |    \ |    \ |
      0----2(pv)----4
      <------. (pvleft)
             .
    '''
    def collect(mverts, mtris, line_index, part_verts):
        base_vi = len(mverts)
        part_tris = [
          [x + base_vi for x in [0, 1, 2]],
          [x + base_vi for x in [2, 1, 3]],
          [x + base_vi for x in [2, 3, 4]],
          [x + base_vi for x in [4, 3, 5]]
          ]
        mverts.extend(part_verts)
        mtris.extend(part_tris)
    mverts = []
    mtris = []
    expand_centerlines(verts, lines, lane_width
                       , lambda li, pv: collect(mverts, mtris, li, pv))
    return (mverts, mtris)


def centerlines_to_polygons(verts, lines, lane_width):
    '''
             line
             .
             .
      <------. (vleft)
      1-----(v)-----3
      |      .      |
      |      .      |
      |      .      |
      0-----(pv)----2
      <------. (pvleft)
             .
    '''
    def collect(mverts, polys, line_index, part_verts):
        base_vi = len(mverts)
        part_polys = [
          [x + base_vi for x in [0, 1, 3, 2]],
          ]
        mverts.extend([part_verts[vi] for vi in [0, 1, 4, 5]])
        mpolys.extend(part_polys)
    mverts = []
    mpolys = []
    expand_centerlines(verts, lines, lane_width
                       , lambda li, pv: collect(mverts, mpolys, li, pv))
    return (mverts, mpolys)


def polygon_union(verts, polys):
    subj = [[verts[i] for i in poly] for poly in polys[:]]
    clip = [verts[i] for i in polys[0]]

    pc = pyclipper.Pyclipper()
    #pc.AddPath(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

    solution = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    uverts = []
    upolys = []

    for pvi, poly_verts in enumerate(solution):
        base_i = len(uverts)
        uverts.extend([[x[0], x[1], 0.0] for x in poly_verts])
        upolys.append(range(base_i, len(uverts)))

    #print uverts, upolys

    return (uverts, upolys)


def write_road_obj(road, obj_file, unproj=CurveUnproj3D(),
                   center=True, yup=True):
    verts, lines, offset = calc_road_obj_polylines(road, unproj, center)
    verts = obj_conv_yup(verts) if yup else verts
    write_obj_polylines(obj_file, verts, lines)


def write_road_obj_mesh(road, obj_file, lane_width, unproj=CurveUnproj3D(),
                        center=True, yup=True):
    verts, lines, offset = calc_road_obj_polylines(road, unproj, center)
    mverts, mfaces = centerlines_to_mesh_simple(verts, lines, lane_width)
    mverts = obj_conv_yup(mverts) if yup else verts
    write_obj_faces(obj_file, mverts, mfaces)
