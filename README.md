# Roller Coaster Designer

## Description

Roller Coaster Designer is a Python desktop application for creating roller coaster tracks and simulating rides. It displays calculated speed and vertical g-force along the track and checks the simulation against configured g-force safety limits.

## Features

- Interactive track editor: drag control points, Shift-click to add a point, or select an interior point and press Delete to remove it.
- Undo and redo track edits with the toolbar buttons or Ctrl+Z/Ctrl+Y.
- Play, Pause, Restart, and Reset Track controls.
- Live coaster speed (mph) and vertical g-force (g) readouts.
- Speed and vertical g-force plots along horizontal track distance.
- G-force limit warnings and a marked failure location.
- Save and Open roller coaster designs as JSON files.
- Export calculated track data to CSV.
- Export a PDF report with design inputs, track/simulation diagrams, results, and safety checks.

**Planned:** No additional features are identified as planned in `spec.md`. Features listed there as out of scope, such as friction, air drag, loops, and multiple cars, are not implemented.

## Requirements

- Python 3.11 or later.
- Tkinter with Tcl/Tk support (normally included with desktop Python distributions).
- External Python packages: Matplotlib and ReportLab.

## Installation

Install Python 3.11 or later from [python.org](https://www.python.org/downloads/) and ensure the installation includes Tcl/Tk support for Tkinter. Open the project directory in Visual Studio Code, then open a terminal in that directory and install the dependencies:

```shell
python -m pip install -r requirements.txt
```

The requirements file installs Matplotlib and ReportLab.

## Running the Application

The Tkinter application entry point is `app.py`. `index.html` is an optional reference to the original application design; it is not integrated into the desktop app and is not needed to run it.
The existing GitHub Pages site remains live as a separate web version served from `index.html`; Pages does not launch or power the Tkinter desktop app.

In Visual Studio Code, use **File → Open Folder** to open the project directory. Open a terminal with **Terminal → New Terminal**, confirm it is in the project directory, and run:

```shell
python app.py
```

## Project Structure

- `app.py` — Tkinter application, track editor, simulation, and file export/import functionality.
- `spec.md` — Application requirements and design specification.
- `AGENTS.md` — Standing instructions for AI coding agents working in this project.
- `prompts.md` — Chronological request and work-outcome log.
- `requirements.txt` — External Python packages needed by the application.
- `index.html` — Optional reference to the original application design; it is not used by the desktop application.
