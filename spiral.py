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

def make_via(cx, cy, r_in):
    v = Via()
    v.position = Vector2.from_xy_mm(cx + r_in, cy)
    v.padstack.drill.diameter = Vector2.from_xy_mm(0.3, 0.3)
    for layer in v.padstack.copper_layers:
        layer.size = Vector2.from_xy_mm(0.6, 0.6)

    return v

def make_test_pads(cx, cy, r_in, p, n, l, width_mm=0.25, layer=BoardLayer.BL_B_Cu):
    t = Track()     # underboard trace
    t.start = Vector2.from_xy(from_mm(cx + r_in), from_mm(cy))
    t.end = Vector2.from_xy(from_mm(cx + r_in + (p * n) + l), from_mm(cy))
    t.start = Vector2.from_xy(from_mm(cx + r_in + (p * n) + l), from_mm(cy))
    t.end = Vector2.from_xy(from_mm(cx + r_in + (p * n) + l + 1), from_mm(cy - 1))

    t.width = from_mm(width_mm)
    t.layer = layer

    return t

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

    tracks = [make_track(a, b) for a, b in zip(pts[:-1], pts[1:])]   # consecutive pairs
    via = [make_via(cx, cy, r_in)]
    test_trace = [make_test_pads(cx, cy, r_in, p, n, l)]

    commit = board.begin_commit()
    board.create_items(tracks)
    board.create_items(via)
    board.create_items(test_trace)

    board.push_commit(commit, input("Enter commit: ") or 'test')

main()