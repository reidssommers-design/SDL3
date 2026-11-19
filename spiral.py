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

SEG = 360 # segments/turn

cx   = float(input('Enter the x center [100]: ') or 100)
cy   = float(input('Enter the y center [100]: ') or 100)    
r_in = float(input('Enter inner radius: ') or 2)       # mm
p    = float(input('Enter the pitch: ') or 0.5)        # mm
N    = int(input('Enter the number of turns: ') or 20) # integer

th = np.linspace(0, 2*np.pi*N, N*SEG + 1)
r  = r_in + (p / (2*np.pi)) * th
pts = list(zip(cx + r*np.cos(th), cy + r*np.sin(th)))
tracks = [make_track(a, b) for a, b in zip(pts[:-1], pts[1:])]   # consecutive pairs

commit = board.begin_commit()
board.create_items(tracks)
board.push_commit(commit, "Add spiral")
