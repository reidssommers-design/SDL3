from kipy import KiCad
from kipy.board_types import Track
from kipy.geometry import Vector2
from kipy.proto.board.board_types_pb2 import BoardLayer
from kipy.util.units import from_mm

# Connect to a running KiCad PCB Editor session
kicad = KiCad()
board = kicad.get_board()

# Create and configure the track
track = Track()
track.start = Vector2.from_xy(from_mm(150), from_mm(70))
track.end = Vector2.from_xy(from_mm(180), from_mm(70))
track.width = from_mm(0.25)
track.layer = BoardLayer.BL_F_Cu

# Push the new track to the board
commit = board.begin_commit()
board.create_items(track)
board.push_commit(commit, "Add trace via Python")

print('Done')
