import numpy as np
from .sequence_curve import SequenceCurve
from .fragment_curve import FragmentCurve
from .straight_curve import StraightCurve


def _link_curve_seq(curve_seq):
    for i in range(1, len(curve_seq)-1):
        curve_seq[i-1].add_outgoing_curve(curve_seq[i])
        curve_seq[i].add_incoming_curve(curve_seq[i-1])
    
def _copy_outgoing_curves(from_curve, copy_outgoing_curve):
    for curve in copy_outgoing_curve.get_outgoing_curves():
        from_curve.add_outgoing_curve(curve)
        
def _link_outgoing(from_curve, outgoing_curve, join_t):
    clean_outgoing_curve = None
    if join_t == 0.0:
        clean_outgoing_curve = outgoing_curve.get_incoming_curve()
    elif join_t < 1.0:
        frag_curve = FragmentCurve(outgoing_curve, join_t, 1.0)
        from_curve.add_outgoing_curve(frag_curve)
        from_curve = frag_curve
        clean_outgoing_curve = outgoing_curve
    else:
        clean_outgoing_curve = outgoing_curve
    _copy_outgoing_curves(from_curve, clean_outgoing_curve)

def build_sampled_interpolation_curve(curve_0, curve_1, seg_length=2.0,
                                        t0_start=0.0, t0_end=1.0,
                                        t1_start=0.0, t1_end=1.0, 
                                        copy_outgoing_curve=None):
    ts = curve_0.sample_t(seg_length, t0_start, t0_end)
    pts = []
    for t in ts:
        interp = (t-t0_start) / (t0_end-t0_start)
        pt_0 = curve_0.t_to_point(t0_start + interp*(t0_end - t0_start))
        pt_1 = curve_1.t_to_point(t1_start + interp*(t1_end - t1_start))
        vec = np.subtract(pt_1, pt_0)
        pts.append(np.add(pt_0, np.multiply(vec, t)))
    segs = []
    if len(pts):
        tail_pt = pts[0]
        for i in range(1, len(pts)-1):
            seg_len = np.linalg.norm(np.subtract(tail_pt, pts[i]))
            if (seg_len > 0.0):
                segs.append(StraightCurve(None, None, tail_pt, pts[i]))
                tail_pt = pts[i]
        _link_curve_seq(segs)
    seq_curve = SequenceCurve(segs)
    if copy_outgoing_curve is not None:
        print('QQQQ')
        _copy_outgoing_curves(seq_curve, copy_outgoing_curve)
    return seq_curve


def build_curve_by_length(init_curve, init_t, length, link_outgoing=False):
    curve_seq = []
    curr_t = init_t
    curr_curve = init_curve
    rest_length = length
    while rest_length > 0.0:
        avail_length = curr_curve.dt_to_length(curr_t, 1.0-curr_t)
        if rest_length > avail_length:
            if avail_length > 0.0:
                curve_seq.append(FragmentCurve(curr_curve, curr_t, 1.0))
            rest_length = rest_length - avail_length
            curr_curve = curr_curve.get_outgoing_curves()[0]
            curr_t = 0.0
            end_t = 0.0
        else:
            end_t = curr_t+curr_curve.length_to_dt(curr_t, rest_length)
            if avail_length > 0.0:
                curve_seq.append(FragmentCurve(curr_curve, curr_t, end_t))
            rest_length = 0
    _link_curve_seq(curve_seq)
    seq_curve = SequenceCurve(curve_seq)
    if link_outgoing and len(curve_seq):
        _link_outgoing(seq_curve, curr_curve, end_t)
    return seq_curve
    