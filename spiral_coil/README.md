# Spiral Inductor — KiCad plugin

Adds a toolbar button to the KiCad PCB Editor that generates a planar Archimedean spiral inductor:

- spiral on F.Cu, return trace on B.Cu, center via
- two test-pad vias sized for a single Dupont / 0.1" header pin each (1.0 mm drill,
  1.7 mm pad, 2.54 mm apart, solder mask opened on both sides)
- Edge.Cuts board outline 6 mm outside all copper
- optional silkscreen info label (board size, trace/gap, turns, L) and title
- live inductance estimate (Mohan current-sheet formula) as you type

> [!WARNING]
> **"Erase entire board first" deletes EVERYTHING on the open board**, not just the spiral:
> footprints, tracks, vias, zones, outline, graphics and text. It is checked by default
> because the tool is meant to regenerate a board dedicated to one coil.
>
> **Only run this on a new, empty board** (File → New, or a scratch project). Never on a
> real project. If you do erase something by accident, press **Ctrl+Z** in KiCad —
> each Refresh is two undo steps (erase, then build).

## Requirements

- **KiCad 9 or newer** (the plugin uses KiCad's IPC API, which older versions don't have)
- **Internet access the first time you click the button** — KiCad downloads the plugin's
  Python packages (`kicad-python`, `numpy`) into a private environment for it

Nothing else to install. The window uses wxPython, which ships with KiCad.

## Install

1. **Download** this repo (green **Code** button → **Download ZIP**) and unzip it.
2. **Copy the `spiral_coil` folder** into KiCad's plugins folder. `<version>` is your KiCad
   version, e.g. `9.0`. Create the `plugins` folder if it isn't there.

   | OS      | Plugins folder |
   |---------|----------------|
   | Windows | `Documents\KiCad\<version>\plugins\` |
   | macOS   | `~/Documents/KiCad/<version>/plugins/` |
   | Linux   | `~/.local/share/kicad/<version>/plugins/` |

   It must end up as `plugins/spiral_coil/plugin.json`, not nested one level deeper.

3. **Turn on the API:** in KiCad, **Preferences → Preferences… → Plugins** → check
   **Enable KiCad API** → OK.
4. **Restart KiCad**, open a board in the PCB Editor, and click the **spiral icon** on the
   top toolbar. The first click takes a little while (KiCad is setting up the plugin's
   Python environment); after that it opens immediately.

## Using it

| Field | Meaning |
|---|---|
| X / Y center | Spiral center on the board (mm, KiCad coordinates — y points down) |
| Inner radius | Radius where the spiral starts (mm) |
| Pitch | Center-to-center distance between turns (mm) |
| Turns | Number of turns (integer) |
| Test pad length | Straight run from the spiral's outer edge to the pads (mm) |
| Width / pitch | Trace width as a fraction of pitch. `0.5` → trace = gap. Must be < 1 |
| Segments / turn | Straight track segments per turn. 360 is smooth |
| Title | Silkscreen text in the upper-right corner. Blank = none |

Press **Refresh board** to build. The L shown is an estimate for an **air-core** coil
(no ferrite nearby), using angle-averaged inner/outer diameters of the spiral. Expect it to
be within a few percent; measure the real board if it matters.

### Starting points

| Use | Inner radius | Pitch | Turns | W | L (approx.) |
|---|---|---|---|---|---|
| Default test coil | 4 | 0.5 | 20 | 0.5 | 7.1 µH |
| NFC tag (NTAG21x, 50 pF) | 14 | 1.0 | 7 | 0.5 | 2.8 µH |

Check your fab's minimum trace/space before ordering — at small pitches the trace and gap
can drop below what cheap fabs make.

## Troubleshooting

- **No button on the toolbar** — check the folder path (step 2), that `plugin.json` is
  directly inside `spiral_coil`, and restart KiCad.
- **"Could not connect to KiCad"** — the API isn't enabled (step 3), or no board is open in
  the PCB Editor.
- **Button does nothing** — in **Preferences → Plugins**, make sure a Python interpreter is
  detected, then restart KiCad. The first launch also needs internet.

## Running from a terminal (optional)

With KiCad open and the API enabled, `spiral.py` also runs on its own with text prompts:

```bash
pip install kicad-python numpy
python spiral.py
```

`mohan.py` on its own is a standalone inductance calculator (`python mohan.py`).
