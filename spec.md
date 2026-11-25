# Roller Coaster Designer — Specification (first draft)

## 1. Purpose

An interactive educational simulator for students and hobbyist coaster designers. Users shape a track, then see how gravity affects a coaster car's speed and the vertical acceleration riders experience.

## 1.1 Platform

The application is a local, single-window Python desktop application.

- **Programming language:** Python 3.11 or later. This is required by the current dependency set: Matplotlib 3.11 requires Python 3.11 or later, and ReportLab 5 requires Python 3.10 or later.
- **User interface:** Tkinter, using its standard widgets, Canvas drawing, and native file dialogs. A Python installation with Tcl/Tk support is required.
- **Operating systems:** Designed for Windows, macOS, and Linux desktop systems where Python and Tkinter are available. Windows is the environment currently verified for this project; macOS and Linux have not been independently tested.
- **External dependencies:** Matplotlib and ReportLab, listed in `requirements.txt`. From the project folder, install them with `python -m pip install -r requirements.txt`. Tkinter and the modules for JSON, CSV, math, temporary files, and date/time are part of Python's standard library.
- **Application entry point:** `app.py`.
- **How to run:** From the project folder, run `python app.py`.
- **File handling:** Save and Open use JSON (`.json`) design files. Simulation data can be exported as CSV (`.csv`) for spreadsheet applications such as Microsoft Excel. Design reports are generated as PDF (`.pdf`) files.
- **Development environment:** A Python 3.11+ installation with pip and Tcl/Tk, plus a terminal and a code editor such as Visual Studio Code. Install dependencies using the command above, then launch with `python app.py`.

Saving and reopening roller coaster designs, CSV simulation exports, and PDF design reports are implemented features.

## 2. Inputs

| Input | Unit | Range/options | Default | Control |
|---|---|---|---|---|
| Track control-point horizontal position | m | 0–100; points remain in left-to-right order | Starter track points | Drag a point on the track canvas |
| Track control-point height | m | 0–60 | Starter track points | Drag a point on the track canvas |
| Playback | — | Play, pause, restart | Paused at the starting crest | Buttons |

The car starts from rest at the first (leftmost) crest. The starting crest is the first control point. The initial model has no friction or air drag.

## 3. Calculations

Use SI units internally. Let `g = 9.81 m/s²`.

- `x` is horizontal track position in metres; `h(x)` is track height above the canvas baseline in metres.
- `h0` is the starting-crest height in metres; the initial car speed is `v0 = 0 m/s`.
- For a frictionless car, conservation of mechanical energy gives `v(x) = sqrt(max(0, v0² + 2g(h0 - h(x))))` in metres per second.
- Convert speed for display using `v_mph = 2.2369362921 v`.
- Let `R` be the local radius of curvature in metres. Define signed curvature `k = 1/R`, positive for a valley (track concave upward) and negative for a crest. The signed vertical g-force is `G = 1 + v²k/g`, measured in multiples of standard gravity. At a valley, this is `1 + v²/(gR)`.
- A car cannot pass a crest above its available energy height: if `h_crest > h0` in the frictionless model, it stops at the preceding reachable point and rolls back.
- A ride fails if signed vertical g-force exceeds `4 g` or falls below `-1 g`. Mark the first failure location on the track.
- Sample the smooth interpolated track to calculate and plot speed and signed vertical g-force along horizontal distance.

## 4. Outputs

- A smooth track, animated car, and marked failure location when the ride fails.
- Live car speed in mph and signed vertical g-force in g.
- A plot of speed (mph) and vertical g-force (g) versus horizontal track distance (m), with the car's current position indicated.
- A visible failure message identifying insufficient energy or a g-force limit violation.

## 5. Look and feel

Show the track editor, ride controls, live readouts, and plots together on the initial screen. Make track points draggable, allow adding points with Shift-click and removing selected interior points, and provide undo/redo for track edits. Provide clear feedback for the starting point and any failure marker. On phones, stack the controls, track, readouts, and plots vertically; keep touch targets large enough to use comfortably.

## 6. Validation

Hand check with `g = 9.81 m/s²`, no friction, a starting crest at `h0 = 30 m`, and a bottom point at `h = 0 m`. The expected speed is `sqrt(2 × 9.81 × (30 - 0)) = sqrt(588.6) = 24.26 m/s = 54.27 mph` (rounded to two decimals).

For a valley radius `R = 20 m` at that bottom point, expected vertical g-force is `1 + 24.26²/(9.81 × 20) = 4.00 g` (rounded to two decimals; calculate using unrounded speed).

## 7. Out of scope

- Real-world structural, aerodynamic, or vehicle design certification.
- Friction, air drag, powered lift hills, loops, thrill scoring, or multiple cars in this first version.
- A guarantee that a designed track is safe for real riders.
