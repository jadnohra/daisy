import numpy as np
from .sequence_curve import SequenceCurve
from .fragment_curve import FragmentCurve
from .straight_curve import StraightCurve


def _link_curve_seq(curve_seq):
    for i in range(1, len(curve_seq)-1):
        curve_seq[i-1].add_outgoing_curve(curve_seq[i])
        curve_seq[i].add_incoming_curve(curve_seq[i-1])


def build_sampled_interpolation_curve(curve_0, curve_1, seg_length=2.0,
                                        t0_start=0.0, t0_end=1.0,
                                        t1_start=0.0, t1_end=1.0):
    ts = curve_0.sample_t(seg_length, t0_start, t0_end)
    print(seg_length, t0_start, t0_end, ts)
    pts = []
    for t in ts:
        interp = (t-t0_start) / (t0_end-t0_start)
        pt_0 = curve_0.t_to_point(t0_start + interp*(t0_end - t0_start))
        pt_1 = curve_1.t_to_point(t1_start + interp*(t1_end - t1_start))
        vec = np.subtract(pt_1, pt_0)
        pts.append(np.add(pt_0, np.multiply(vec, t)))
    segs = []
    for i in range(len(pts)-1):
        segs.append(StraightCurve(None, None, pts[i], pts[i+1]))
    _link_curve_seq(segs)
    return SequenceCurve(segs)


def build_curve_by_length(init_curve, init_t, length):
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
            curr_curve = init_curve.get_outgoing_curves()[0]
            curr_t = 0.0
        else:
            end_t = curr_t+curr_curve.length_to_dt(curr_t, rest_length)
            if avail_length > 0.0:
                curve_seq.append(FragmentCurve(curr_curve, curr_t, end_t))
            rest_length = 0
    _link_curve_seq(curve_seq)
    return SequenceCurve(curve_seq)