# Roller Coaster Designer — First Draft

## Features

The required app will let a user shape a coaster track, simulate a car, and inspect speed and vertical g-force. In addition to those must-haves, I propose:

- **Design comparison:** save one track as a baseline and compare another track's ride and telemetry with it.
- **Keyboard track editing:** select a control point and move it with arrow keys as an alternative to dragging.

These features are planned for after the must-have ride and its validation work.

## 1. Purpose

An interactive, single-page learning tool for students and coaster enthusiasts to design a 2D track and see how gravity affects a car's speed and rider g-force.

## 2. Inputs

- Track control points: drag the points on the track canvas to shape the path. The first point is the starting crest.
- Ride controls: start, pause, and reset the animation.
- Comparison controls: save the current design as the comparison baseline or clear the baseline.
- Keyboard alternative: select a control point and use arrow keys to move it.

The app uses standard gravity and starts with an example track. The revised spec will set exact ranges, defaults, and control behavior.

## 3. Calculations

Assume no friction. Let \(g=9.81\ \mathrm{m/s^2}\), \(h_0\) be the starting height, and \(h\) the car's current height, both in meters:

\[
v=\sqrt{2g(h_0-h)}
\]

Convert speed from meters per second to miles per hour. Compute vertical g-force from the track's slope and signed curvature; at a horizontal valley with radius \(R\) in meters:

\[
n=1+\frac{v^2}{gR}
\]

The car rolls back if it cannot reach a crest. Mark a failure if vertical g-force exceeds \(4g\) or falls below \(-1g\).

## 4. Outputs

Show the editable track, animated car, speed in mph, vertical g-force, and plots of speed and g-force along the track. Mark the failure point and report whether the car rolled back or exceeded a g-force limit. Comparison outputs will be specified in the revision.

## 5. Look and feel

Use one responsive page with the track editor and ride controls above the live readouts and plots. Open with an example track ready to simulate. Keep controls touch-friendly on phones.

## 6. Validation

With no friction, compare the app's bottom-of-drop speed to \(v=\sqrt{2g(h_0-h)}\). At a valley, compare its vertical g-force to \(n=1+v^2/(gR)\). Exact test inputs and expected values will be added in the revised spec.

## 7. Out of scope

The initial simulation will not model friction, air drag, lift hills, loops as specialized track elements, or real-world structural design. It is an educational approximation, not a safety certification.
