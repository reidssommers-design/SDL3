from kipy import KiCad
from kipy.board_types import Track
from kipy.geometry import Vector2
from kipy.proto.board.board_types_pb2 import BoardLayer
from kipy.util.units import from_mm

import numpy as np

# Connect to a running KiCad PCB Editor session
kicad = KiCad()
board = kicad.get_board()

def make_track(p0, p1, width_mm=0.25, layer=BoardLayer.BL_F_Cu):
    t = Track()
    t.start = Vector2.from_xy(from_mm(p0[0]), from_mm(p0[1]))
    t.end   = Vector2.from_xy(from_mm(p1[0]), from_mm(p1[1]))
    t.width = from_mm(width_mm)
    t.layer = layer
    return t

# stairstep: (x, y) in mm
pts = [(150, 70), (160, 70), (160, 80), (170, 80), (170, 90), (180, 90)]

tracks = [make_track(a, b) for a, b in zip(pts[:-1], pts[1:])]   # consecutive pairs

commit = board.begin_commit()
board.create_items(tracks)          # one call for the whole list
board.push_commit(commit, "Add stairstep")
