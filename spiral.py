from kipy import KiCad
from kipy.board_types import Track, Via
from kipy.geometry import Vector2
from kipy.proto.board.board_types_pb2 import BoardLayer
from kipy.util.units import from_mm

import numpy as np

# Connect to a running KiCad PCB Editor session
kicad = KiCad()
board = kicad.get_board()

SEG = 360 # segments/turn

def make_track(p0, p1, width_mm=0.25, layer=BoardLayer.BL_F_Cu):
    t = Track()
    t.start = Vector2.from_xy(from_mm(p0[0]), from_mm(p0[1]))
    t.end   = Vector2.from_xy(from_mm(p1[0]), from_mm(p1[1]))
    t.width = from_mm(width_mm)
    t.layer = layer
    return t

def make_polyline(pts, width_mm=0.25, layer=BoardLayer.BL_F_Cu):
    return [make_track(a, b, width_mm, layer) for a, b in zip(pts[:-1], pts[1:])]

def make_via(x, y, drill_mm=0.3, pad_mm=0.6):
    v = Via()
    v.position = Vector2.from_xy_mm(x, y)
    v.padstack.drill.diameter = Vector2.from_xy_mm(drill_mm, drill_mm)
    for layer in v.padstack.copper_layers:
        layer.size = Vector2.from_xy_mm(pad_mm, pad_mm)

    return v

def make_test_pads(cx, cy, r_in, p, n, l, spiral_end, width_mm=0.25):
    x_ext = cx + r_in + p*n + l
    bot_pts = [
        (cx + r_in, cy),
        (x_ext,     cy),
        (x_ext + 1, cy - 1),
    ]

    sx, sy = spiral_end
    top_pts = [
        (sx,        sy),
        (x_ext,     cy),
        (x_ext + 1, cy + 1),
    ]

    tracks = (make_polyline(bot_pts, width_mm, BoardLayer.BL_B_Cu) +
              make_polyline(top_pts, width_mm, BoardLayer.BL_F_Cu))

    # test pad vias at the end of each trace
    pads = [make_via(*bot_pts[-1], drill_mm=0.6, pad_mm=1.2),
            make_via(*top_pts[-1], drill_mm=0.6, pad_mm=1.2)]

    return tracks, pads

def get_params():
    cx   = float(input('Enter the x center [100]: ') or 100)
    cy   = float(input('Enter the y center [100]: ') or 100)
    r_in = float(input('Enter inner radius: ') or 2)       # mm
    p    = float(input('Enter the pitch: ') or 0.5)        # mm
    n    = int(input('Enter the number of turns: ') or 20) # integer

    l    = float(input('Enter the length of test pad: ') or 5)

    return cx, cy, r_in, p, n, l

def calc_spiral(cx, cy, r_in, p, n):
    th = np.linspace(0, 2*np.pi*n, n*SEG + 1)
    r  = r_in + (p / (2*np.pi)) * th
    pts = list(zip(cx + r*np.cos(th), cy + r*np.sin(th)))

    return pts

def main():
    cx, cy, r_in, p, n, l = get_params()

    pts = calc_spiral(cx, cy, r_in, p, n)

    tracks = make_polyline(pts)
    via = [make_via(cx + r_in, cy)]
    test_trace, test_pads = make_test_pads(cx, cy, r_in, p, n, l, pts[-1])

    commit = board.begin_commit()
    board.create_items(tracks)
    board.create_items(via)
    board.create_items(test_trace)
    board.create_items(test_pads)

    board.push_commit(commit, input("Enter commit: ") or 'test')

main()