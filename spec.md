# Roller Coaster Designer — Revised Specification

## Features

Build the required editor, energy-based ride, readouts, plots, and failure detection first. After those pass the validation case below, add these two features:

1. **Design comparison:** let the user save the current track and its calculated ride as one in-memory baseline. The user can then compare another design against it using overlaid track and telemetry plots and a table of maximum speed, minimum vertical g-force, and maximum vertical g-force. The baseline lasts until cleared or the page is reloaded. This is an original design-comparison feature, not one of the suggested ideas.
2. **Keyboard track editing:** allow the user to select a control point and move it with arrow keys as an alternative to dragging. Each arrow press moves it 1 m along the relevant axis; Shift plus an arrow moves it 10 m. Do not allow a move outside the input ranges or past a neighboring point's horizontal position.

These features are not part of the must-have validation gate and must be implemented only after the required ride passes it.

## 1. Purpose

Roller Coaster Designer is an educational, single-page web app for students and coaster enthusiasts. It lets them shape a two-dimensional track and explore how gravitational potential energy, track curvature, and rider vertical g-force change during a ride. It is an idealized physics model, not an engineering or safety-certification tool.

## 2. Inputs

| Input | Meaning and unit | Allowed range | Default | Control |
|---|---|---|---|---|
| Track control-point horizontal position, \(x_i\) | Horizontal distance from the track's left edge, in meters | 0–500 m; points must remain in their existing left-to-right order with no equal adjacent positions | The nine points listed below | Drag a point horizontally with a mouse or touch. The planned keyboard-editing feature also supports arrow keys. |
| Track control-point height, \(h_i\) | Height above the track editor's zero datum, in meters | 0–100 m | The nine points listed below | Drag a point vertically with a mouse or touch. The planned keyboard-editing feature also supports arrow keys. |
| Ride command | Start, pause, or reset the current ride | Start and pause toggle; reset returns to the start | The car is stopped at the start | Buttons |
| Comparison command (planned feature) | Save the current design as the comparison baseline, or clear the baseline | One baseline at a time | No baseline | Save and Clear buttons |

The default track control points, in \((x_i,h_i)\) meters, are:

\[
(0,30),\ (10,20),\ (20,10),\ (30,2.5),\ (40,0),\
(50,2.5),\ (60,10),\ (70,22.5),\ (80,27)
\]

There are always nine control points; users shape the track by moving them. The first point is the starting crest, and its height is \(h_0\). Gravity is a fixed physical constant, not a user input. An invalid drag is not applied; the editor keeps the last valid track and explains the constraint.

## 3. Calculations

### Track and ride

- Fit a uniform Catmull–Rom cubic spline through the nine control points. Sample it at intervals no greater than 0.5 m of track arc length. The sample distance \(s\) is the distance traveled along the curve, in meters. Reject edits that make the spline leave the editor's 0–100 m height range or make horizontal position cease to increase.
- Use standard gravity \(g=9.81\ \mathrm{m/s^2}\). There is no friction or air drag.
- Let \(h_0\) be the first control point's height and \(h\) the car's current height, both in meters. Conservation of mechanical energy gives speed \(v\) in meters per second:

\[
v=\sqrt{2g(h_0-h)}
\]

This is defined only for \(h\le h_0\). Convert to miles per hour using
\[
v_{\mathrm{mph}}=2.2369362920544v.
\]

- Let \(\theta\) be the local track tangent angle from horizontal, in radians, and let \(\kappa\) be signed curvature in \(\mathrm{m^{-1}}\), positive for a valley (concave upward) and negative for a crest. The vertical rider load \(n\), dimensionless and displayed in g, is
\[
n=\cos(\theta)+\frac{v^2\kappa}{g}.
\]
At the bottom of a horizontal valley, \(\theta=0\) and \(\kappa=1/R\), so this reduces to the requested check:
\[
n=1+\frac{v^2}{gR},
\]
where \(R\) is the valley's radius of curvature in meters.

### Failure rules

- **Insufficient energy:** if the track rises above \(h_0\), the car turns around at the first uphill location where \(h=h_0\). Mark that turning point as a rollback failure; the car does not continue through the higher crest.
- **Unsafe vertical load:** mark failure at the first location where \(n>4\) or \(n<-1\). Values exactly equal to either limit are allowed. Interpolate between adjacent samples to place the marker at the estimated threshold crossing.
- If more than one failure condition would occur, show the earliest one along the direction of travel. Stop the forward animation at that point and report whether it was a rollback, an upper g-force limit, or a lower g-force limit.
- Recompute the spline, energy values, curvature, g-force, plots, and failure location after a valid track edit. An edit during playback pauses the ride before recomputing it.

## 4. Outputs

- A labeled two-dimensional track editor with all nine draggable control points, the smooth spline, and a car marker.
- Start, Pause, and Reset controls.
- Live speed in mph and vertical rider load in g at the car's current location.
- A speed plot in mph and a vertical-g-force plot in g, each against distance along the track in meters.
- A visible failure marker on both the track and plots, with a concise failure reason. If no failure occurs before the track ends, show that no failure was detected on the modeled track.
- For the planned comparison feature, an overlaid baseline track and plots plus a table comparing maximum speed (mph), minimum vertical load (g), and maximum vertical load (g).

## 5. Look and feel

Use a single responsive page. On a wide screen, put the track editor and ride controls across the top and the live readouts and two plots below. Keep the editor's axes labeled in meters and distinguish the car and failure marker from the track and control points. On a phone, stack the editor, controls, readouts, and plots vertically; keep buttons and drag targets large enough for touch and prevent the page from requiring horizontal scrolling.

When first opened, show the default nine-point track, the car at its starting point, speed at 0 mph, and the calculated starting vertical load. The ride is stopped until the user presses Start. Pause freezes the car; Reset returns it to the first point and clears the current ride's failure state.

## 6. Validation

Use this exact validation track, with the nine points in \((x_i,h_i)\) meters:

\[
(0,30),\ (10,20),\ (20,10),\ (30,2.5),\ (40,0),\
(50,2.5),\ (60,10),\ (70,22.5),\ (80,40)
\]

The first point is the starting crest, so \(h_0=30\ \mathrm{m}\). At the valley point \((40,0)\), \(h=0\ \mathrm{m}\), \(g=9.81\ \mathrm{m/s^2}\), and the track is horizontal. The equal-spaced neighboring spline points give a valley curvature of \(0.05\ \mathrm{m^{-1}}\), so \(R=20\ \mathrm{m}\).

Hand calculation:

\[
v=\sqrt{2(9.81)(30-0)}
 =\sqrt{588.6}
 \approx24.261\ \mathrm{m/s}
 \]
\[
v_{\mathrm{mph}}=24.261(2.2369362920544)\approx54.27\ \mathrm{mph}
 \]
\[
n=1+\frac{(24.261)^2}{(9.81)(20)}
 =1+\frac{588.6}{196.2}
 =4.00\ \mathrm{g}
\]

Expected app results at the valley, rounded to two decimal places: **54.27 mph** and **4.00 g**. The valley itself is not a g-force failure because the rule is strictly above 4 g. This track later rises above the 30 m starting height, so the app should also mark a rollback where the car first reaches \(h=30\ \mathrm{m}\) on that climb. Compare the app's computed location and readouts with these hand results before implementing either planned feature.

## 7. Out of scope

- Friction, rolling resistance, air drag, powered or lift hills, and energy loss.
- Loops or special track elements, three-dimensional tracks, banking, lateral g-force, and multi-car operation.
- Structural analysis, real-world ride certification, or claims that a design is safe for riders.
- Saving designs to a server, accounts, or cross-device synchronization. The planned comparison baseline is temporary and exists only in the current page session.
