# Roller Coaster Designer

A single-file browser simulator for exploring how track height and curvature affect a coaster car's speed and vertical g-force. Open `index.html` in a modern browser.

The public repository also retains a separate legacy Tkinter version in `app.py`; it is not required by or integrated with this web app.

## Editing a track

- Drag a blue control point to change its position or height.
- Shift-click the track to insert a new point. Points stay in left-to-right order with at least 2 m between them.
- Select an interior point and choose **Remove point** or press **Delete**. The first and last points cannot be removed.
- Use **Undo** and **Redo**, or **Ctrl/Cmd+Z**, **Ctrl/Cmd+Y**, and **Ctrl/Cmd+Shift+Z**. A new edit clears the redo history.
- **Reset track** restores the starter design. Track edits are also saved in the current browser profile until its site data is cleared.

## Ride and file actions

Use **Play ride**, **Pause ride**, and **Restart** to run the frictionless simulation. The **File** menu saves and opens versioned JSON coaster files. **Export CSV** downloads sampled ride data, including horizontal and cumulative track distance, speed, height, g-force, curvature, and reachability. **Ride report PDF** downloads a calculation sheet with a track diagram, ride inputs, results, and model-limit checks.

This version models a single-valued height profile; vertical loop geometry, friction, and air drag are not supported. The simulator is educational and does not certify real rides as safe.
