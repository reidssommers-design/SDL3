from kipy import KiCad
from kipy.board_types import Track, Via, BoardRectangle, BoardText
from kipy.geometry import Vector2
from kipy.proto.board.board_types_pb2 import BoardLayer, SolderMaskMode
from kipy.proto.common.types.enums_pb2 import HorizontalAlignment, VerticalAlignment
from kipy.util.units import from_mm

import numpy as np

import mohan

# Connect to a running KiCad PCB Editor session
kicad = KiCad()
board = kicad.get_board()

SEG = 360 # segments/turn
W   = 0.5 # trace width as a fraction of pitch (0.5 -> trace = gap)

def make_track(p0, p1, width_mm=0.25, layer=BoardLayer.BL_F_Cu):
    t = Track()
    t.start = Vector2.from_xy(from_mm(p0[0]), from_mm(p0[1]))
    t.end   = Vector2.from_xy(from_mm(p1[0]), from_mm(p1[1]))
    t.width = from_mm(width_mm)
    t.layer = layer
    return t

def make_polyline(pts, width_mm=0.25, layer=BoardLayer.BL_F_Cu):
    return [make_track(a, b, width_mm, layer) for a, b in zip(pts[:-1], pts[1:])]

def make_via(x, y, drill_mm=0.3, pad_mm=0.6, mask_mm=None):
    v = Via()
    v.position = Vector2.from_xy_mm(x, y)
    v.padstack.drill.diameter = Vector2.from_xy_mm(drill_mm, drill_mm)
    for layer in v.padstack.copper_layers:
        layer.size = Vector2.from_xy_mm(pad_mm, pad_mm)

    if mask_mm is not None:     # untent both sides, opening = pad + 2*mask_mm
        v.padstack.front_outer_layers.solder_mask_mode = SolderMaskMode.SMM_UNMASKED
        v.padstack.front_outer_layers.solder_mask_settings.solder_mask_margin = from_mm(mask_mm)

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
    pads = [make_via(*bot_pts[-1], drill_mm=0.6, pad_mm=1.2, mask_mm=0.5),
            make_via(*top_pts[-1], drill_mm=0.6, pad_mm=1.2, mask_mm=0.5)]

    return tracks, pads

def make_outline(tracks, vias, margin_mm=6, line_mm=0.1):
    # bounding box of all copper (nm), including trace half-widths and via pad radii
    xs, ys = [], []
    for t in tracks:
        h = t.width // 2
        for pt in (t.start, t.end):
            xs += [pt.x - h, pt.x + h]
            ys += [pt.y - h, pt.y + h]
    for v in vias:
        h = v.padstack.copper_layers[0].size.x // 2
        xs += [v.position.x - h, v.position.x + h]
        ys += [v.position.y - h, v.position.y + h]

    m = from_mm(margin_mm)
    edge = BoardRectangle()
    edge.top_left     = Vector2.from_xy(min(xs) - m, min(ys) - m)
    edge.bottom_right = Vector2.from_xy(max(xs) + m, max(ys) + m)
    edge.layer = BoardLayer.BL_Edge_Cuts
    edge.attributes.stroke.width = from_mm(line_mm)
    edge.attributes.fill.filled = False

    return edge

def make_label(edge, w, p, n, L, size_mm=1.0, inset_mm=1.0):
    # silkscreen info block, anchored to the outline's lower-right corner
    bw = (edge.bottom_right.x - edge.top_left.x) / 1e6     # nm -> mm
    bh = (edge.bottom_right.y - edge.top_left.y) / 1e6

    t = BoardText()
    t.value = (f'{bw:.1f} x {bh:.1f} mm\n'
               f'w {w:.2f} / s {p - w:.2f} mm\n'
               f'N = {n}\n'
               f'L = {L*1e6:.2f} µH')
    t.layer = BoardLayer.BL_F_SilkS

    inset = from_mm(inset_mm)
    t.position = Vector2.from_xy(edge.bottom_right.x - inset, edge.bottom_right.y - inset)

    a = t.attributes
    a.multiline = True
    a.line_spacing = 1.0        # proto default is 0 -> all lines drawn on top of each other
    a.size = Vector2.from_xy_mm(size_mm, size_mm)
    a.stroke_width = from_mm(0.15)
    a.horizontal_alignment = HorizontalAlignment.HA_RIGHT
    a.vertical_alignment   = VerticalAlignment.VA_BOTTOM

    return t

def make_title(edge, text, size_mm=1.5, inset_mm=1.0):
    # silkscreen title, anchored to the outline's upper-right corner
    t = BoardText()
    t.value = text
    t.layer = BoardLayer.BL_F_SilkS

    inset = from_mm(inset_mm)
    t.position = Vector2.from_xy(edge.bottom_right.x - inset, edge.top_left.y + inset)

    a = t.attributes
    a.multiline = True          # '\n' in the title would technically work
    a.line_spacing = 1.0
    a.size = Vector2.from_xy_mm(size_mm, size_mm)
    a.stroke_width = from_mm(0.2)
    a.horizontal_alignment = HorizontalAlignment.HA_RIGHT
    a.vertical_alignment   = VerticalAlignment.VA_TOP

    return t

def get_params():
    cx   = float(input('Enter the x center [100]: ') or 100)
    cy   = float(input('Enter the y center [100]: ') or 100)
    r_in = float(input('Enter inner radius: ') or 2)       # mm
    p    = float(input('Enter the pitch: ') or 0.5)        # mm
    n    = int(input('Enter the number of turns: ') or 20) # integer

    l    = float(input('Enter the length of test pad: ') or 5)

    label = (input('Print info label? (y/n) [y]: ') or 'y') == 'y'
    title = input('Title (blank for none): ').strip()

    return cx, cy, r_in, p, n, l, label, title

def calc_spiral(cx, cy, r_in, p, n):
    th = np.linspace(0, 2*np.pi*n, n*SEG + 1)
    r  = r_in + (p / (2*np.pi)) * th
    pts = list(zip(cx + r*np.cos(th), cy + r*np.sin(th)))

    return pts

def erase_board():
    items = (
        board.get_footprints()
        + board.get_tracks()
        + board.get_vias()
        + board.get_zones()
        + board.get_shapes()
        + board.get_text()
    )

    commit = board.begin_commit()
    board.remove_items(items)
    board.push_commit(commit, "Erase entire PCB")

def build(cx, cy, r_in, p, n, l, label=True, title='', msg='test'):
    w = W * p   # mm, single source for every trace width below

    L = mohan.from_spiral(r_in, p, n, w)
    print(f'L = {L*1e6:.4f} µH')

    pts = calc_spiral(cx, cy, r_in, p, n)

    tracks = make_polyline(pts, w)
    via = [make_via(cx + r_in, cy)]
    test_trace, test_pads = make_test_pads(cx, cy, r_in, p, n, l, pts[-1], w)

    commit = board.begin_commit()
    board.create_items(tracks)
    board.create_items(via)
    board.create_items(test_trace)
    board.create_items(test_pads)
    edge = make_outline(tracks + test_trace, via + test_pads)
    board.create_items([edge])
    if label:
        board.create_items([make_label(edge, w, p, n, L)])
    if title:
        board.create_items([make_title(edge, title)])

    board.push_commit(commit, msg)

    return L

def main():
    erase = input('Do you want to erase the board? (yes/n) ')
    if erase == 'yes':
        erase_board()

    cx, cy, r_in, p, n, l, label, title = get_params()
    msg = input("Enter commit: ") or 'test'

    build(cx, cy, r_in, p, n, l, label, title, msg)

if __name__ == '__main__':
    main()