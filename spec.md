# Roller Coaster Designer — Specification

## 1. Purpose

An interactive educational simulator for students and hobbyist coaster designers. Users shape a track, then see how gravity affects a coaster car's speed and the vertical acceleration riders experience.

## 2. Inputs

| Input | Unit | Range/options | Default | Control |
|---|---|---|---|---|
| Track control-point horizontal position | m | 0–100; at least 2 m between points | Starter track points | Drag a point; Shift-click the canvas to insert one |
| Track control-point height | m | 0–60 | Starter track points | Drag a point; select an interior point to remove it |
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

Show the track editor, ride controls, live readouts, and plots together on the initial screen. Make track points draggable and provide clear feedback for the starting point, selected point, and any failure marker. On phones, stack the controls, track, readouts, and plots vertically; keep touch targets large enough to use comfortably.

## 6. Features

- **Persistent track autosave (original feature):** Save edited control points in the browser and restore them when the app is opened again in the same browser profile. Show whether the current design was restored or saved. The design remains available unless browser site data is cleared.
- **Track editing and recovery:** Shift-click to insert a control point at the clicked position; select an interior point and remove it without removing either endpoint. Undo and redo track edits with buttons or Ctrl/Cmd+Z, Ctrl/Cmd+Y, and Ctrl/Cmd+Shift+Z. Keep the edit history bounded and clear redo history when a new edit is made.
- **Design files:** A File menu saves the supported track points, fixed ride settings, starting position, and current car position to a versioned JSON design file. Open validates the file and restores the design with playback paused. Loop geometry is not part of this version's height-profile model.
- **Ride data export:** Export sampled horizontal distance, cumulative track distance, speed, height, signed vertical g-force, curvature, and reachability to an Excel-compatible CSV file.
- **Ride calculation sheet:** Generate a one-page PDF with the ride inputs, track diagram, key calculated results, energy and g-force checks, and an educational-use disclaimer.

## 7. Validation

Hand check with `g = 9.81 m/s²`, no friction, a starting crest at `h0 = 30 m`, and a bottom point at `h = 0 m`. The expected speed is `sqrt(2 × 9.81 × (30 - 0)) = sqrt(588.6) = 24.26 m/s = 54.27 mph` (rounded to two decimals).

For a valley radius `R = 20 m` at that bottom point, expected vertical g-force is `1 + 24.26²/(9.81 × 20) = 4.00 g` (rounded to two decimals; calculate using unrounded speed).

For persistence, move a control point, reload the page, and confirm the same point is restored. Then undo a drag and reset the track, confirming the readouts and plots recalculate after each action.

For editing history, Shift-click between existing points, verify order and spacing are preserved, remove the selected interior point, and verify both operations can be undone and redone with buttons and keyboard shortcuts. Confirm endpoints cannot be removed and a new edit clears the redo history.

For design files, save an edited design, reopen it, and verify all supported track points and car position are restored. Confirm malformed or unsupported files produce a visible error. For exports, check that the CSV includes each sampled track location and the PDF includes the requested summary metrics, track diagram, and both safety checks.

## 8. Out of scope

- Real-world structural, aerodynamic, or vehicle design certification.
- Friction, air drag, powered lift hills, loops, thrill scoring, or multiple cars in this first version.
- A guarantee that a designed track is safe for real riders.
