import wx

import mohan

# key, label, default, type
FIELDS = [
    ('cx',   'X center (mm)',        100,  float),
    ('cy',   'Y center (mm)',        100,  float),
    ('r_in', 'Inner radius (mm)',    4,    float),
    ('p',    'Pitch (mm)',           0.5,  float),
    ('n',    'Turns',                20,   int),
    ('l',    'Test pad length (mm)', 5,    float),
    ('W',    'Width / pitch',        0.5,  float),
    ('SEG',  'Segments / turn',      360,  int),
]

class SpiralFrame(wx.Frame):
    def __init__(self, spiral):
        super().__init__(None, title='Spiral inductor',
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.spiral = spiral
        self.erase_confirmed = False

        pnl = wx.Panel(self)
        grid = wx.FlexGridSizer(cols=2, vgap=4, hgap=10)

        self.entries = {}
        for key, label, default, _ in FIELDS:
            grid.Add(wx.StaticText(pnl, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            ctrl = wx.TextCtrl(pnl, value=str(default), size=(90, -1))
            ctrl.Bind(wx.EVT_TEXT, self.update_L)      # live L as you type
            grid.Add(ctrl)
            self.entries[key] = ctrl

        grid.Add(wx.StaticText(pnl, label='Title (blank = none)'), 0, wx.ALIGN_CENTER_VERTICAL)
        self.title = wx.TextCtrl(pnl, size=(160, -1))
        grid.Add(self.title)

        self.L_text = wx.StaticText(pnl, label='')
        f = self.L_text.GetFont()
        f.SetWeight(wx.FONTWEIGHT_BOLD)
        f.SetPointSize(f.GetPointSize() + 1)
        self.L_text.SetFont(f)

        self.erase = wx.CheckBox(pnl, label='Erase entire board first')
        self.erase.SetValue(True)
        self.label = wx.CheckBox(pnl, label='Info label')
        self.label.SetValue(True)
        checks = wx.BoxSizer(wx.HORIZONTAL)
        checks.Add(self.erase, 0, wx.RIGHT, 15)
        checks.Add(self.label)

        btn = wx.Button(pnl, label='Refresh board')
        btn.Bind(wx.EVT_BUTTON, self.refresh)

        self.status = wx.StaticText(pnl, label='')
        self.status.SetForegroundColour(wx.Colour(128, 128, 128))

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(grid, 0, wx.ALL, 10)
        box.Add(self.L_text, 0, wx.ALIGN_CENTER | wx.TOP, 4)
        box.Add(checks, 0, wx.ALL, 10)
        box.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        box.Add(self.status, 0, wx.ALIGN_CENTER | wx.ALL, 8)
        pnl.SetSizer(box)
        box.Fit(self)

        self.update_L()

    def read(self):
        # parsed values, raises ValueError on bad input
        # typ(float(...)) so '20' and '20.0' both work for int fields
        return {key: typ(float(self.entries[key].GetValue())) for key, _, _, typ in FIELDS}

    def update_L(self, _evt=None):
        try:
            v = self.read()
        except ValueError:
            self.L_text.SetLabel('L = —')       # half-typed field, wait for more input
        else:
            try:
                L = mohan.from_spiral(v['r_in'], v['p'], v['n'], v['W'] * v['p'])
                self.L_text.SetLabel(f'L = {L*1e6:.4f} µH')
            except (ValueError, ZeroDivisionError) as e:
                self.L_text.SetLabel(f'L = —  ({e})')
        self.Layout()

    def refresh(self, _evt):
        try:
            v = self.read()
        except ValueError:
            wx.MessageBox('Every field must be a number.', 'Bad input', wx.ICON_ERROR, self)
            return

        if self.erase.GetValue() and not self.erase_confirmed:
            ok = wx.MessageBox('"Erase entire board first" deletes EVERYTHING on the open board '
                               '(footprints, tracks, zones, outline, text), not just the spiral.\n\n'
                               'Continue? (Ctrl+Z in KiCad undoes it.)',
                               'Erase board?', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self)
            if ok != wx.YES:
                return
            self.erase_confirmed = True     # only ask once per session

        self.spiral.W   = v['W']      # module globals read by build() / calc_spiral()
        self.spiral.SEG = v['SEG']

        self.status.SetLabel('Working...')
        wx.Yield()
        try:
            with wx.BusyCursor():
                if self.erase.GetValue():
                    self.spiral.erase_board()
                L = self.spiral.build(v['cx'], v['cy'], v['r_in'], v['p'], v['n'], v['l'],
                                      label=self.label.GetValue(),
                                      title=self.title.GetValue().strip(),
                                      msg='Spiral GUI refresh')
            self.status.SetLabel(f'Board updated  (L = {L*1e6:.4f} µH)')
        except Exception as e:
            self.status.SetLabel('Failed')
            wx.MessageBox(str(e), 'KiCad error', wx.ICON_ERROR, self)
        self.Layout()

def main():
    app = wx.App()
    try:
        import spiral       # connects to KiCad on import
    except Exception as e:
        wx.MessageBox('Could not connect to KiCad.\n\n'
                      'Open a board in the PCB Editor and make sure '
                      'Preferences > Plugins > "Enable KiCad API" is checked.\n\n'
                      f'Details: {e}', 'Spiral inductor', wx.ICON_ERROR)
        return

    frame = SpiralFrame(spiral)
    frame.Show()
    frame.Raise()
    app.MainLoop()

if __name__ == '__main__':
    main()
