import tkinter as tk
from tkinter import ttk, messagebox

import spiral       # connects to KiCad on import
import mohan

# key, label, default, type
FIELDS = [
    ('cx',   'X center (mm)',        100,        float),
    ('cy',   'Y center (mm)',        100,        float),
    ('r_in', 'Inner radius (mm)',    4,          float),
    ('p',    'Pitch (mm)',           0.5,        float),
    ('n',    'Turns',                20,         int),
    ('l',    'Test pad length (mm)', 5,          float),
    ('W',    'Width / pitch',        spiral.W,   float),
    ('SEG',  'Segments / turn',      spiral.SEG, int),
]

root = tk.Tk()
root.title('Spiral inductor')

frm = ttk.Frame(root, padding=10)
frm.grid()

entries = {}
for i, (key, label, default, _) in enumerate(FIELDS):
    ttk.Label(frm, text=label).grid(row=i, column=0, sticky='w', padx=(0, 10))
    var = tk.StringVar(value=str(default))
    ttk.Entry(frm, textvariable=var, width=10).grid(row=i, column=1)
    entries[key] = var

row = len(FIELDS)

L_text = tk.StringVar()
ttk.Label(frm, textvariable=L_text, font=('TkDefaultFont', 11, 'bold')).grid(
    row=row, column=0, columnspan=2, pady=(10, 0))

erase = tk.BooleanVar(value=True)
ttk.Checkbutton(frm, text='Erase board first', variable=erase).grid(
    row=row + 1, column=0, columnspan=2, sticky='w', pady=(10, 0))

status = tk.StringVar()
ttk.Label(frm, textvariable=status, foreground='gray').grid(
    row=row + 3, column=0, columnspan=2)

def read():
    # parsed values, raises ValueError on bad input
    # typ(float(...)) so '20' and '20.0' both work for int fields
    return {key: typ(float(entries[key].get())) for key, _, _, typ in FIELDS}

def update_L(*_):
    try:
        v = read()
    except ValueError:
        L_text.set('L = —')         # half-typed field, wait for more input
        return
    try:
        L = mohan.from_spiral(v['r_in'], v['p'], v['n'], v['W'] * v['p'])
        L_text.set(f'L = {L*1e6:.4f} µH')
    except (ValueError, ZeroDivisionError) as e:
        L_text.set(f'L = —  ({e})')

def refresh():
    try:
        v = read()
    except ValueError:
        messagebox.showerror('Bad input', 'Every field must be a number.')
        return

    spiral.W   = v['W']      # module globals read by build() / calc_spiral()
    spiral.SEG = v['SEG']

    status.set('Working...')
    root.update_idletasks()
    try:
        if erase.get():
            spiral.erase_board()
        L = spiral.build(v['cx'], v['cy'], v['r_in'], v['p'], v['n'], v['l'],
                         msg='Spiral GUI refresh')
        status.set(f'Board updated  (L = {L*1e6:.4f} µH)')
    except Exception as e:
        status.set('Failed')
        messagebox.showerror('KiCad error', str(e))

ttk.Button(frm, text='Refresh board', command=refresh).grid(
    row=row + 2, column=0, columnspan=2, pady=10, sticky='ew')

for var in entries.values():
    var.trace_add('write', update_L)    # live L as you type
update_L()

root.mainloop()