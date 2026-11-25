import math
import json
import csv
import tempfile
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
import matplotlib.pyplot as plt


G = 9.81
MPS_TO_MPH = 2.2369362921


class CubicSpline:
    def __init__(self, xs, ys):
        self.xs = list(xs)
        self.ys = list(ys)
        self.n = len(xs)
        self.coefficients = self._natural_spline()

    def _natural_spline(self):
        n = self.n
        h = [self.xs[i + 1] - self.xs[i] for i in range(n - 1)]
        alpha = [0.0] * n
        for i in range(1, n - 1):
            alpha[i] = (
                3.0
                / h[i]
                * (self.ys[i + 1] - self.ys[i])
                - 3.0
                / h[i - 1]
                * (self.ys[i] - self.ys[i - 1])
            )

        l = [1.0] * n
        mu = [0.0] * n
        z = [0.0] * n
        c = [0.0] * n
        b = [0.0] * (n - 1)
        d = [0.0] * (n - 1)

        for i in range(1, n - 1):
            l[i] = 2.0 * (self.xs[i + 1] - self.xs[i - 1]) - h[i - 1] * mu[i - 1]
            mu[i] = h[i] / l[i]
            z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i]

        for j in range(n - 2, -1, -1):
            c[j] = z[j] - mu[j] * c[j + 1]
            b[j] = (
                (self.ys[j + 1] - self.ys[j]) / h[j]
                - h[j] * (c[j + 1] + 2.0 * c[j]) / 3.0
            )
            d[j] = (c[j + 1] - c[j]) / (3.0 * h[j])

        return b, c, d

    def segment_index(self, x):
        x = max(self.xs[0], min(self.xs[-1], x))
        for i in range(self.n - 2):
            if x <= self.xs[i + 1]:
                return i
        return self.n - 2

    def evaluate(self, x):
        i = self.segment_index(x)
        dx = x - self.xs[i]
        b, c, d = self.coefficients
        return self.ys[i] + b[i] * dx + c[i] * dx * dx + d[i] * dx * dx * dx

    def derivative(self, x):
        i = self.segment_index(x)
        dx = x - self.xs[i]
        b, c, d = self.coefficients
        return b[i] + 2.0 * c[i] * dx + 3.0 * d[i] * dx * dx

    def second_derivative(self, x):
        i = self.segment_index(x)
        dx = x - self.xs[i]
        _, c, d = self.coefficients
        return 2.0 * c[i] + 6.0 * d[i] * dx


def calculate_ride(
    track_points,
    sample_count=801,
    gravity=G,
    maximum_g=4.0,
    minimum_g=-1.0,
    initial_speed=0.0,
):
    xs = [point[0] for point in track_points]
    ys = [point[1] for point in track_points]
    spline = CubicSpline(xs, ys)
    h0 = ys[0]
    samples = []
    failure = None
    insufficient_energy = False
    x_values = [xs[0] + (xs[-1] - xs[0]) * i / (sample_count - 1) for i in range(sample_count)]

    for x in x_values:
        height = spline.evaluate(x)
        speed = math.sqrt(
            max(
                0.0,
                initial_speed * initial_speed
                + 2.0 * gravity * (h0 - height),
            )
        )

        dy = spline.derivative(x)
        ddy = spline.second_derivative(x)
        denominator = (1.0 + dy * dy) ** 1.5
        curvature = 0.0 if denominator == 0.0 else ddy / denominator
        g_force = 1.0 + speed * speed * curvature / gravity

        if height > h0 + 1e-6:
            insufficient_energy = True
            if failure is None:
                failure = (x, height, "Insufficient energy: the track rises above the starting height")
        if (g_force > maximum_g or g_force < minimum_g) and failure is None:
            failure = (
                x,
                height,
                f"G-force limit violation: {g_force:.2f} g",
            )

        samples.append((x, height, speed, g_force))

    reachable_limit = None
    if insufficient_energy:
        first_too_high_index = next(
            (i for i, sample in enumerate(samples) if sample[1] > h0 + 1e-6),
            len(samples),
        )
        reachable_limit = samples[max(0, first_too_high_index - 1)][0]

    return spline, samples, failure, reachable_limit


class RollerCoasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roller Coaster Designer")
        self.root.geometry("1180x760")
        self.root.minsize(900, 620)

        self.track_points = [
            (0.0, 30.0),
            (15.0, 24.0),
            (32.0, 8.0),
            (50.0, 4.0),
            (68.0, 16.0),
            (84.0, 12.0),
            (100.0, 22.0),
        ]
        self.gravity = G
        self.maximum_g = 4.0
        self.minimum_g = -1.0
        self.initial_speed = 0.0
        self.friction_enabled = False
        self.air_drag_enabled = False
        self.current_file = None
        self.drag_index = None
        self.drag_start_points = None
        self.selected_point_index = None
        self.undo_stack = []
        self.redo_stack = []
        self.running = False
        self.car_x = 0.0
        self.animation_id = None
        self.last_time = None

        self._build_ui()
        self._recalculate()

    def _build_ui(self):
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("Status.TLabel", padding=8)

        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Save", command=self.save_design)
        file_menu.add_command(label="Open", command=self.open_design)
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_command(label="Export PDF Report", command=self.export_pdf)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.configure(menu=menubar)

        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=3)
        main.rowconfigure(2, weight=2)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)

        title = ttk.Frame(main)
        title.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(title, text="Roller Coaster Designer", font=("TkDefaultFont", 18, "bold")).pack(side="left")
        ttk.Label(title, text="Shape a track, then see how gravity affects the ride.", foreground="#4a5568").pack(
            side="left", padx=12
        )

        track_frame = ttk.LabelFrame(main, text="Track editor")
        track_frame.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=(0, 8), pady=8)
        track_frame.rowconfigure(0, weight=1)
        track_frame.columnconfigure(0, weight=1)
        self.track_canvas = tk.Canvas(track_frame, background="#eef6fb", highlightthickness=0)
        self.track_canvas.grid(row=0, column=0, sticky="nsew")
        self.track_canvas.bind("<Configure>", lambda event: self._recalculate())
        self.track_canvas.bind("<ButtonPress-1>", self._start_drag)
        self.track_canvas.bind("<B1-Motion>", self._drag)
        self.track_canvas.bind("<ButtonRelease-1>", self._finish_drag)
        self.track_canvas.bind("<Shift-Button-1>", self._add_control_point)
        self.track_canvas.bind("<Delete>", self._delete_selected_point)
        self.track_canvas.bind("<BackSpace>", self._delete_selected_point)
        self.root.bind("<Control-z>", self.undo_track)
        self.root.bind("<Control-y>", self.redo_track)
        self.root.bind("<Control-Shift-Z>", self.redo_track)

        edit_toolbar = ttk.Frame(track_frame)
        edit_toolbar.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        ttk.Label(
            edit_toolbar,
            text="Drag to shape · Shift-click to add · select + Delete to remove",
            foreground="#64748b",
        ).pack(side="left", padx=(2, 12))
        self.undo_button = ttk.Button(edit_toolbar, text="Undo", command=self.undo_track)
        self.undo_button.pack(side="right", padx=(4, 0))
        self.redo_button = ttk.Button(edit_toolbar, text="Redo", command=self.redo_track)
        self.redo_button.pack(side="right", padx=(4, 0))
        self.remove_point_button = ttk.Button(
            edit_toolbar,
            text="Remove Point",
            command=self._delete_selected_point,
        )
        self.remove_point_button.pack(side="right", padx=(4, 0))

        right = ttk.Frame(main)
        right.grid(row=1, column=1, sticky="nsew", pady=8)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        controls = ttk.LabelFrame(right, text="Ride controls")
        controls.grid(row=0, column=0, sticky="ew")
        for column in range(6):
            controls.columnconfigure(column, weight=1)
        self.play_button = ttk.Button(controls, text="Play", command=self.toggle_play)
        self.play_button.grid(row=0, column=0, padx=5, pady=8)
        ttk.Button(controls, text="Pause", command=self.pause).grid(row=0, column=1, padx=5, pady=8)
        ttk.Button(controls, text="Restart", command=self.restart).grid(row=0, column=2, padx=5, pady=8)
        ttk.Button(controls, text="Reset track", command=self.reset_track).grid(row=0, column=3, padx=5, pady=8)
        ttk.Button(controls, text="Export CSV", command=self.export_csv).grid(row=0, column=4, padx=5, pady=8)
        ttk.Button(controls, text="Export PDF", command=self.export_pdf).grid(row=0, column=5, padx=5, pady=8)

        readout = ttk.LabelFrame(right, text="Live readouts")
        readout.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        readout.columnconfigure(0, weight=1)
        readout.columnconfigure(1, weight=1)
        self.speed_value = tk.StringVar(value="0.00 mph")
        self.g_value = tk.StringVar(value="1.00 g")
        ttk.Label(readout, text="Speed", foreground="#64748b").grid(row=0, column=0, padx=12, pady=(12, 0))
        ttk.Label(readout, text="Vertical g-force", foreground="#64748b").grid(row=0, column=1, padx=12, pady=(12, 0))
        ttk.Label(readout, textvariable=self.speed_value, font=("TkDefaultFont", 15, "bold")).grid(
            row=1, column=0, padx=12, pady=(0, 12)
        )
        ttk.Label(readout, textvariable=self.g_value, font=("TkDefaultFont", 15, "bold")).grid(
            row=1, column=1, padx=12, pady=(0, 12)
        )
        self.status_label = ttk.Label(
            readout,
            text="Paused at the starting crest",
            style="Status.TLabel",
            anchor="center",
        )
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))

        plot_frame = ttk.LabelFrame(main, text="Plots")
        plot_frame.grid(row=2, column=1, sticky="nsew", pady=8)
        plot_frame.rowconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)
        self.plot_canvas = tk.Canvas(plot_frame, background="white", highlightthickness=0)
        self.plot_canvas.grid(row=0, column=0, sticky="nsew")
        self.plot_canvas.bind("<Configure>", lambda event: self._recalculate())

    def _track_bounds(self):
        width = max(1, self.track_canvas.winfo_width())
        height = max(1, self.track_canvas.winfo_height())
        left, right = 55, width - 25
        top, bottom = 25, height - 38
        return left, right, top, bottom

    def _to_canvas(self, x, height):
        left, right, top, bottom = self._track_bounds()
        cx = left + (x / 100.0) * (right - left)
        cy = bottom - (height / 60.0) * (bottom - top)
        return cx, cy

    def _from_canvas(self, cx, cy):
        left, right, top, bottom = self._track_bounds()
        x = (cx - left) / (right - left) * 100.0
        height = (bottom - cy) / (bottom - top) * 60.0
        return max(0.0, min(100.0, x)), max(0.0, min(60.0, height))

    def _recalculate(self):
        self.spline, self.samples, self.failure, self.reachable_limit = calculate_ride(
            self.track_points,
            gravity=self.gravity,
            maximum_g=self.maximum_g,
            minimum_g=self.minimum_g,
            initial_speed=self.initial_speed,
        )
        self._draw_track()
        self._draw_plots()
        self._update_live_readout()
        self._update_edit_controls()

    def _draw_track(self):
        canvas = self.track_canvas
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        left, right, top, bottom = self._track_bounds()

        canvas.create_rectangle(left, top, right, bottom, fill="#ffffff", outline="#cbd5e1")
        for value in range(0, 61, 10):
            _, cy = self._to_canvas(0, value)
            canvas.create_line(left, cy, right, cy, fill="#e2e8f0")
            canvas.create_text(left - 8, cy, text=str(value), anchor="e", fill="#64748b", font=("TkDefaultFont", 8))
        for value in range(0, 101, 20):
            cx, _ = self._to_canvas(value, 0)
            canvas.create_line(cx, bottom, cx, bottom + 5, fill="#94a3b8")
            canvas.create_text(cx, bottom + 14, text=str(value), anchor="n", fill="#64748b", font=("TkDefaultFont", 8))
        canvas.create_text((left + right) / 2, height - 7, text="Horizontal distance (m)", fill="#475569")
        canvas.create_text(12, (top + bottom) / 2, text="Height (m)", fill="#475569")

        if len(self.samples) > 1:
            points = []
            for x, track_height, _, _ in self.samples:
                cx, cy = self._to_canvas(x, track_height)
                points.extend((cx, cy))
            canvas.create_line(points, fill="#2563eb", width=4, smooth=True)

        for i, (x, track_height) in enumerate(self.track_points):
            cx, cy = self._to_canvas(x, track_height)
            fill = "#f97316" if i == 0 else "#2563eb"
            outline = "#7c3aed" if i == self.selected_point_index else "#9a3412" if i == 0 else "#1e40af"
            radius = 10 if i == self.selected_point_index else 7
            canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill=fill,
                outline=outline,
                width=3 if i == self.selected_point_index else 2,
            )
            canvas.create_text(cx, cy - 13, text=str(i + 1), fill="#334155", font=("TkDefaultFont", 8, "bold"))

        if self.failure is not None:
            x, track_height, _ = self.failure
            cx, cy = self._to_canvas(x, track_height)
            canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="#dc2626", outline="#7f1d1d", width=2)
            canvas.create_text(cx, cy - 18, text="!", fill="#dc2626", font=("TkDefaultFont", 12, "bold"))

        car_x = max(self.track_points[0][0], min(self.reachable_limit or self.track_points[-1][0], self.car_x))
        car_y = self.spline.evaluate(car_x)
        cx, cy = self._to_canvas(car_x, car_y)
        canvas.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, fill="#facc15", outline="#713f12", width=2)

    def _draw_plots(self):
        canvas = self.plot_canvas
        canvas.delete("all")
        width = max(1, canvas.winfo_width())
        height = max(1, canvas.winfo_height())
        left, right = 50, width - 20
        top, bottom = 18, height - 35

        canvas.create_rectangle(left, top, right, bottom, fill="#ffffff", outline="#cbd5e1")
        for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
            cy = bottom - fraction * (bottom - top)
            canvas.create_line(left, cy, right, cy, fill="#e2e8f0")
        for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
            cx = left + fraction * (right - left)
            canvas.create_line(cx, bottom, cx, bottom + 5, fill="#94a3b8")
            canvas.create_text(cx, bottom + 13, text=f"{fraction * 100:.0f}", anchor="n", fill="#64748b", font=("TkDefaultFont", 8))
        canvas.create_text((left + right) / 2, height - 8, text="Distance (m)", fill="#475569")

        speed_points = []
        g_points = []
        max_speed = max(1.0, max(sample[2] * MPS_TO_MPH for sample in self.samples))
        for x, _, speed, g_force in self.samples:
            cx = left + x / 100.0 * (right - left)
            cy_speed = bottom - (speed * MPS_TO_MPH / max_speed) * (bottom - top)
            cy_g = bottom - ((g_force + 1.0) / 5.0) * (bottom - top)
            speed_points.extend((cx, cy_speed))
            g_points.extend((cx, cy_g))

        canvas.create_line(speed_points, fill="#2563eb", width=2)
        canvas.create_line(g_points, fill="#dc2626", width=2)

        legend_y = top + 12
        canvas.create_line(right - 145, legend_y, right - 125, legend_y, fill="#2563eb", width=3)
        canvas.create_text(right - 118, legend_y, text="Speed (mph)", anchor="w", fill="#334155", font=("TkDefaultFont", 8))
        canvas.create_line(right - 145, legend_y + 16, right - 125, legend_y + 16, fill="#dc2626", width=3)
        canvas.create_text(right - 118, legend_y + 16, text="g-force (g)", anchor="w", fill="#334155", font=("TkDefaultFont", 8))

        car_x = max(self.track_points[0][0], min(self.reachable_limit or self.track_points[-1][0], self.car_x))
        cx = left + car_x / 100.0 * (right - left)
        canvas.create_line(cx, top, cx, bottom, fill="#facc15", width=2)

    def _update_live_readout(self):
        car_x = max(self.track_points[0][0], min(self.reachable_limit or self.track_points[-1][0], self.car_x))
        height = self.spline.evaluate(car_x)
        speed = math.sqrt(
            max(
                0.0,
                self.initial_speed * self.initial_speed
                + 2.0 * self.gravity * (self.track_points[0][1] - height),
            )
        )

        dy = self.spline.derivative(car_x)
        ddy = self.spline.second_derivative(car_x)
        curvature = ddy / ((1.0 + dy * dy) ** 1.5)
        g_force = 1.0 + speed * speed * curvature / self.gravity

        self.speed_value.set(f"{speed * MPS_TO_MPH:.2f} mph")
        self.g_value.set(f"{g_force:.2f} g")

        if self.reachable_limit is not None:
            self.status_label.configure(
                text=f"Insufficient energy — stopping near {self.reachable_limit:.1f} m",
                foreground="#b91c1c",
            )
        elif self.failure is not None:
            self.status_label.configure(text=self.failure[2], foreground="#b91c1c")
        elif self.running:
            self.status_label.configure(text="Ride in progress", foreground="#1d4ed8")
        else:
            self.status_label.configure(text="Paused at the starting crest", foreground="#475569")

    def _update_edit_controls(self):
        if not hasattr(self, "undo_button"):
            return
        self.undo_button.configure(state="normal" if self.undo_stack else "disabled")
        self.redo_button.configure(state="normal" if self.redo_stack else "disabled")
        can_remove = (
            self.selected_point_index is not None
            and 0 < self.selected_point_index < len(self.track_points) - 1
        )
        self.remove_point_button.configure(state="normal" if can_remove else "disabled")

    def _record_track_edit(self):
        self.undo_stack.append(list(self.track_points))
        if len(self.undo_stack) > 100:
            del self.undo_stack[0]
        self.redo_stack.clear()

    def _add_control_point(self, event):
        left, right, top, bottom = self._track_bounds()
        if not (left <= event.x <= right and top <= event.y <= bottom):
            return "break"

        x, _ = self._from_canvas(event.x, event.y)
        if any(abs(x - point_x) < 1.0 for point_x, _ in self.track_points):
            messagebox.showinfo(
                "Point Too Close",
                "New control points must be at least 1 m from existing points.",
                parent=self.root,
            )
            return "break"

        height = max(0.0, min(60.0, self.spline.evaluate(x)))
        insertion_index = next(
            (index for index, (point_x, _) in enumerate(self.track_points) if point_x > x),
            len(self.track_points),
        )
        self._record_track_edit()
        self.track_points.insert(insertion_index, (x, height))
        self.selected_point_index = insertion_index
        self.restart()
        return "break"

    def _delete_selected_point(self, event=None):
        index = self.selected_point_index
        if index is None or index <= 0 or index >= len(self.track_points) - 1:
            return "break" if event is not None else None
        self._record_track_edit()
        self.track_points.pop(index)
        self.selected_point_index = None
        self.restart()
        return "break" if event is not None else None

    def undo_track(self, event=None):
        if not self.undo_stack:
            return "break" if event is not None else None
        self.redo_stack.append(list(self.track_points))
        self.track_points = self.undo_stack.pop()
        self.selected_point_index = None
        self.restart()
        return "break" if event is not None else None

    def redo_track(self, event=None):
        if not self.redo_stack:
            return "break" if event is not None else None
        self.undo_stack.append(list(self.track_points))
        self.track_points = self.redo_stack.pop()
        self.selected_point_index = None
        self.restart()
        return "break" if event is not None else None

    def _start_drag(self, event):
        if event.state & 0x0001:
            return "break"
        self.track_canvas.focus_set()
        left, right, top, bottom = self._track_bounds()
        if not (left <= event.x <= right and top <= event.y <= bottom):
            return
        nearest = None
        nearest_distance = 12
        for i, (x, track_height) in enumerate(self.track_points):
            cx, cy = self._to_canvas(x, track_height)
            distance = math.hypot(event.x - cx, event.y - cy)
            if distance < nearest_distance:
                nearest = i
                nearest_distance = distance
        if nearest is not None:
            self.drag_index = nearest
            self.selected_point_index = nearest
            self.drag_start_points = list(self.track_points)
            self._draw_track()
            self.pause()
        else:
            self.selected_point_index = None
            self._update_edit_controls()
            self._draw_track()

    def _drag(self, event):
        if self.drag_index is None:
            return
        x, height = self._from_canvas(event.x, event.y)
        i = self.drag_index
        if i == 0:
            x = 0.0
        elif i == len(self.track_points) - 1:
            x = 100.0
        else:
            x = max(self.track_points[i - 1][0] + 1.0, min(self.track_points[i + 1][0] - 1.0, x))
        self.track_points[i] = (x, height)
        self.restart()

    def _finish_drag(self, event):
        if self.drag_start_points is not None and self.drag_start_points != self.track_points:
            self.undo_stack.append(self.drag_start_points)
            if len(self.undo_stack) > 100:
                del self.undo_stack[0]
            self.redo_stack.clear()
        self.drag_start_points = None
        self.drag_index = None
        self._update_edit_controls()

    def save_design(self):
        filename = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save Roller Coaster Design",
            defaultextension=".json",
            filetypes=[("Roller coaster JSON", "*.json"), ("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="roller-coaster-design.json",
        )
        if not filename:
            return

        design = {
            "format": "roller-coaster-designer",
            "version": 1,
            "track": {
                "control_points": [
                    {"x": float(x), "height": float(height)}
                    for x, height in self.track_points
                ]
            },
            "physics": {
                "gravity_mps2": float(self.gravity),
                "initial_speed_mps": float(self.initial_speed),
                "friction_enabled": bool(self.friction_enabled),
                "air_drag_enabled": bool(self.air_drag_enabled),
            },
            "safety": {
                "maximum_g": float(self.maximum_g),
                "minimum_g": float(self.minimum_g),
            },
            "playback": {
                "car_position_m": float(self.car_x),
                "paused": not bool(self.running),
            },
        }

        try:
            with open(filename, "w", encoding="utf-8") as design_file:
                json.dump(design, design_file, indent=2)
            self.current_file = filename
            self.root.title(f"Roller Coaster Designer - {filename}")
        except (OSError, TypeError, ValueError) as error:
            messagebox.showerror("Save Failed", f"Could not save the design:\n{error}", parent=self.root)

    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export Roller Coaster Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="roller-coaster-data.csv",
        )
        if not filename:
            return

        try:
            with open(filename, "w", encoding="utf-8-sig", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["x", "Height", "Speed", "Vertical g-force"])
                for x, height, speed_mps, g_force in self.samples:
                    writer.writerow(
                        [
                            f"{x:.6f}",
                            f"{height:.6f}",
                            f"{speed_mps * MPS_TO_MPH:.6f}",
                            f"{g_force:.6f}",
                        ]
                    )
        except (OSError, csv.Error, TypeError, ValueError) as error:
            messagebox.showerror("Export Failed", f"Could not export the CSV:\n{error}", parent=self.root)

    def export_pdf(self):
        filename = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export Roller Coaster PDF Report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="roller-coaster-design-report.pdf",
        )
        if not filename:
            return

        try:
            violations = [
                (x, g_force)
                for x, _, _, g_force in self.samples
                if g_force > self.maximum_g or g_force < self.minimum_g
            ]
            insufficient = [
                (x, height)
                for x, height, _, _ in self.samples
                if height > self.track_points[0][1] + 1e-6
            ]

            speeds_mph = [speed * MPS_TO_MPH for _, _, speed, _ in self.samples]
            g_forces = [g_force for _, _, _, g_force in self.samples]
            maximum_speed = max(speeds_mph)
            maximum_g_force = max(g_forces)
            minimum_g_force = min(g_forces)
            satisfies_limits = not violations and not insufficient

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "ReportTitle",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=22,
                textColor=colors.HexColor("#1e3a5f"),
                alignment=TA_CENTER,
                spaceAfter=12,
            )
            heading_style = ParagraphStyle(
                "SectionHeading",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=14,
                textColor=colors.HexColor("#1e3a5f"),
                spaceBefore=8,
                spaceAfter=8,
            )
            body_style = ParagraphStyle(
                "ReportBody",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
            )

            def header_footer(canvas, document):
                canvas.saveState()
                canvas.setFillColor(colors.HexColor("#1e3a5f"))
                canvas.rect(0, letter[1] - 34, letter[0], 34, fill=1, stroke=0)
                canvas.setFillColor(colors.white)
                canvas.setFont("Helvetica-Bold", 10)
                canvas.drawString(36, letter[1] - 22, "Roller Coaster Designer")
                canvas.setFillColor(colors.HexColor("#64748b"))
                canvas.setFont("Helvetica", 8)
                canvas.drawString(36, 20, "Simulation report")
                canvas.drawRightString(letter[0] - 36, 20, f"Page {document.page}")
                canvas.restoreState()

            document = SimpleDocTemplate(
                filename,
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=48,
                bottomMargin=36,
                title="Roller Coaster Design Report",
                author="Roller Coaster Designer",
            )

            story = [
                Spacer(1, 18),
                Paragraph("Roller Coaster Design Report", title_style),
                Paragraph(
                    f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                    ParagraphStyle(
                        "Subtitle",
                        parent=body_style,
                        alignment=TA_CENTER,
                        textColor=colors.HexColor("#64748b"),
                    ),
                ),
                Spacer(1, 16),
                Paragraph("Design Inputs", heading_style),
            ]

            input_rows = [
                ["Setting", "Value"],
                ["Gravity", f"{self.gravity:.3f} m/s²"],
                ["Initial speed", f"{self.initial_speed:.3f} m/s"],
                ["Maximum g-force", f"{self.maximum_g:.3f} g"],
                ["Minimum g-force", f"{self.minimum_g:.3f} g"],
                ["Friction", "Disabled" if not self.friction_enabled else "Enabled"],
                ["Air drag", "Disabled" if not self.air_drag_enabled else "Enabled"],
                ["Track points", str(len(self.track_points))],
            ]
            input_table = Table(input_rows, colWidths=[2.2 * inch, 4.2 * inch], repeatRows=1)
            input_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.extend([input_table, Spacer(1, 12), Paragraph("Track Control Points", heading_style)])

            point_rows = [["Point", "Horizontal position (m)", "Height (m)"]]
            point_rows.extend(
                [str(index + 1), f"{x:.3f}", f"{height:.3f}"]
                for index, (x, height) in enumerate(self.track_points)
            )
            point_table = Table(point_rows, colWidths=[0.7 * inch, 2.6 * inch, 2.6 * inch], repeatRows=1)
            point_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.extend([point_table, Spacer(1, 12), Paragraph("Results Summary", heading_style)])

            status_text = "SATISFIES SPECIFIED SAFETY LIMITS" if satisfies_limits else "DOES NOT SATISFY SPECIFIED SAFETY LIMITS"
            status_color = "#166534" if satisfies_limits else "#991b1b"
            summary_rows = [
                ["Metric", "Value"],
                ["Maximum speed", f"{maximum_speed:.2f} mph"],
                ["Maximum vertical g-force", f"{maximum_g_force:.2f} g"],
                ["Minimum vertical g-force", f"{minimum_g_force:.2f} g"],
                ["Safety status", status_text],
            ]
            summary_table = Table(summary_rows, colWidths=[2.2 * inch, 4.2 * inch], repeatRows=1)
            summary_style = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
            summary_style.append(("TEXTCOLOR", (1, 4), (1, 4), colors.HexColor(status_color)))
            summary_style.append(("FONTNAME", (1, 4), (1, 4), "Helvetica-Bold"))
            summary_table.setStyle(TableStyle(summary_style))
            story.append(summary_table)

            with tempfile.TemporaryDirectory() as temporary_directory:
                track_path = f"{temporary_directory}/track.png"
                speed_path = f"{temporary_directory}/speed.png"
                g_path = f"{temporary_directory}/gforce.png"

                xs = [x for x, _, _, _ in self.samples]
                heights = [height for _, height, _, _ in self.samples]
                plt.style.use("seaborn-v0_8-whitegrid")

                fig, axis = plt.subplots(figsize=(7.2, 3.8))
                axis.plot(xs, heights, color="#2563eb", linewidth=2.5)
                axis.scatter(
                    [x for x, _ in self.track_points],
                    [height for _, height in self.track_points],
                    color="#2563eb",
                    edgecolor="#1e3a8a",
                    s=45,
                    zorder=3,
                )
                if self.failure is not None:
                    failure_x, failure_height, _ = self.failure
                    axis.scatter([failure_x], [failure_height], color="#dc2626", s=90, marker="X", zorder=4)
                axis.set_title("Complete Roller Coaster Track", fontsize=13, fontweight="bold")
                axis.set_xlabel("Horizontal position (m)")
                axis.set_ylabel("Height (m)")
                axis.set_xlim(0, 100)
                axis.set_ylim(0, 60)
                fig.tight_layout()
                fig.savefig(track_path, dpi=180, bbox_inches="tight")
                plt.close(fig)

                fig, axis = plt.subplots(figsize=(7.2, 3.8))
                axis.plot(xs, speeds_mph, color="#2563eb", linewidth=2)
                axis.fill_between(xs, 0, speeds_mph, color="#bfdbfe", alpha=0.5)
                axis.set_title("Coaster Speed Throughout the Ride", fontsize=13, fontweight="bold")
                axis.set_xlabel("Horizontal position (m)")
                axis.set_ylabel("Speed (mph)")
                axis.set_xlim(0, 100)
                axis.set_ylim(bottom=0)
                fig.tight_layout()
                fig.savefig(speed_path, dpi=180, bbox_inches="tight")
                plt.close(fig)

                fig, axis = plt.subplots(figsize=(7.2, 3.8))
                axis.plot(xs, g_forces, color="#dc2626", linewidth=2)
                axis.axhline(self.maximum_g, color="#b45309", linestyle="--", linewidth=1.5, label=f"Maximum: {self.maximum_g:.2f} g")
                axis.axhline(self.minimum_g, color="#7c3aed", linestyle="--", linewidth=1.5, label=f"Minimum: {self.minimum_g:.2f} g")
                if violations:
                    axis.scatter(
                        [x for x, _ in violations],
                        [g for _, g in violations],
                        color="#dc2626",
                        s=20,
                        zorder=3,
                        label="Exceedance",
                    )
                axis.set_title("Vertical G-Force Throughout the Ride", fontsize=13, fontweight="bold")
                axis.set_xlabel("Horizontal position (m)")
                axis.set_ylabel("Vertical g-force (g)")
                axis.set_xlim(0, 100)
                axis.legend(loc="best", fontsize=8)
                fig.tight_layout()
                fig.savefig(g_path, dpi=180, bbox_inches="tight")
                plt.close(fig)

                story.extend([PageBreak(), Paragraph("Track Diagram", heading_style), Image(track_path, width=6.8 * inch, height=3.55 * inch)])
                story.extend([PageBreak(), Paragraph("Speed Diagram", heading_style), Image(speed_path, width=6.8 * inch, height=3.55 * inch)])
                story.extend([PageBreak(), Paragraph("G-Force Diagram", heading_style), Image(g_path, width=6.8 * inch, height=3.55 * inch)])

                story.extend([Spacer(1, 10), Paragraph("Safety Checks", heading_style)])
                if violations:
                    violation_rows = [["Location (m)", "G-force (g)", "Limit exceeded"]]
                    violation_rows.extend(
                        [
                            f"{x:.3f}",
                            f"{g_force:.3f}",
                            "Above maximum" if g_force > self.maximum_g else "Below minimum",
                        ]
                        for x, g_force in violations
                    )
                    violation_table = Table(violation_rows, colWidths=[1.6 * inch, 1.6 * inch, 3.2 * inch], repeatRows=1)
                    violation_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#991b1b")),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                                ("FONTSIZE", (0, 0), (-1, -1), 8),
                                ("ALIGN", (0, 1), (-1, -1), "CENTER"),
                                ("TOPPADDING", (0, 0), (-1, -1), 4),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                            ]
                        )
                    )
                    story.append(violation_table)
                else:
                    story.append(
                        Paragraph(
                            f"No locations exceed the configured g-force limits ({self.minimum_g:.2f} g to {self.maximum_g:.2f} g).",
                            body_style,
                        )
                    )

                if insufficient:
                    start_x = insufficient[0][0]
                    story.append(
                        Spacer(1, 8)
                    )
                    story.append(
                        Paragraph(
                            f"Insufficient energy warning: the track rises above the starting height beginning near {start_x:.3f} m.",
                            body_style,
                        )
                    )
                document.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
        except (OSError, ImportError, ValueError, RuntimeError) as error:
            messagebox.showerror("PDF Export Failed", f"Could not create the PDF report:\n{error}", parent=self.root)

    def open_design(self):
        filename = filedialog.askopenfilename(
            parent=self.root,
            title="Open Roller Coaster Design",
            filetypes=[("Roller coaster JSON", "*.json"), ("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as design_file:
                design = json.load(design_file)
            track_points = self._validate_design(design)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            messagebox.showerror("Open Failed", f"Could not open the design:\n{error}", parent=self.root)
            return

        physics = design["physics"]
        safety = design["safety"]
        playback = design.get("playback", {})
        self.track_points = track_points
        self.gravity = float(physics["gravity_mps2"])
        self.initial_speed = float(physics["initial_speed_mps"])
        self.friction_enabled = bool(physics["friction_enabled"])
        self.air_drag_enabled = bool(physics["air_drag_enabled"])
        self.maximum_g = float(safety["maximum_g"])
        self.minimum_g = float(safety["minimum_g"])
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.selected_point_index = None
        self.current_file = filename
        self.running = False
        self.play_button.configure(text="Play")
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        restored_position = float(playback.get("car_position_m", 0.0))
        self.car_x = max(track_points[0][0], min(track_points[-1][0], restored_position))
        self.root.title(f"Roller Coaster Designer - {filename}")
        self._recalculate()

    def _validate_design(self, design):
        if not isinstance(design, dict):
            raise ValueError("The file root must be a JSON object.")
        if design.get("format") != "roller-coaster-designer":
            raise ValueError("This is not a Roller Coaster Designer file.")

        track = design.get("track")
        physics = design.get("physics")
        safety = design.get("safety")
        if not isinstance(track, dict) or not isinstance(physics, dict) or not isinstance(safety, dict):
            raise ValueError("The file must contain track, physics, and safety sections.")

        control_points = track.get("control_points")
        if not isinstance(control_points, list) or len(control_points) < 2:
            raise ValueError("The track must contain at least two control points.")

        track_points = []
        previous_x = -1.0
        for point in control_points:
            if not isinstance(point, dict):
                raise ValueError("Each control point must be a JSON object.")
            x = float(point["x"])
            height = float(point["height"])
            if not math.isfinite(x) or not math.isfinite(height):
                raise ValueError("Control point coordinates must be finite numbers.")
            if x < previous_x or x < 0.0 or x > 100.0 or height < 0.0 or height > 60.0:
                raise ValueError("Control points must be ordered from left to right within track limits.")
            track_points.append((x, height))
            previous_x = x

        if track_points[0][0] != 0.0 or track_points[-1][0] != 100.0:
            raise ValueError("The first control point must be at 0 m and the last at 100 m.")

        gravity = float(physics["gravity_mps2"])
        initial_speed = float(physics["initial_speed_mps"])
        maximum_g = float(safety["maximum_g"])
        minimum_g = float(safety["minimum_g"])
        if not math.isfinite(gravity) or gravity <= 0.0:
            raise ValueError("Gravity must be a finite positive number.")
        if not math.isfinite(initial_speed) or initial_speed < 0.0:
            raise ValueError("Initial speed must be a finite non-negative number.")
        if not math.isfinite(maximum_g) or not math.isfinite(minimum_g) or minimum_g > maximum_g:
            raise ValueError("G-force limits must be finite, with the minimum below the maximum.")
        if bool(physics.get("friction_enabled", False)) or bool(physics.get("air_drag_enabled", False)):
            raise ValueError("This app version does not support friction or air-drag settings.")

        return track_points

    def toggle_play(self):
        if self.running:
            self.pause()
        else:
            self.running = True
            self.last_time = None
            self.play_button.configure(text="Playing")
            self._animate()

    def pause(self):
        self.running = False
        self.play_button.configure(text="Play")
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self._recalculate()

    def restart(self):
        self.running = False
        self.play_button.configure(text="Play")
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.car_x = 0.0
        self._recalculate()

    def reset_track(self):
        default_track = [
            (0.0, 30.0),
            (15.0, 24.0),
            (32.0, 8.0),
            (50.0, 4.0),
            (68.0, 16.0),
            (84.0, 12.0),
            (100.0, 22.0),
        ]
        if self.track_points != default_track:
            self._record_track_edit()
            self.track_points = default_track
        self.selected_point_index = None
        self.restart()

    def _animate(self):
        if not self.running:
            return
        now = self.root.after(16, lambda: None)
        if self.last_time is None:
            self.last_time = 0
        height = self.spline.evaluate(self.car_x)
        speed_mps = math.sqrt(
            max(
                0.0,
                self.initial_speed * self.initial_speed
                + 2.0 * self.gravity * (self.track_points[0][1] - height),
            )
        )
        scale = 0.28
        self.car_x += max(0.08, speed_mps * scale)

        limit = self.reachable_limit if self.reachable_limit is not None else self.track_points[-1][0]
        if self.car_x >= limit:
            self.car_x = limit
            self.running = False
            self.play_button.configure(text="Play")
            self.status_label.configure(
                text="Ride finished" if self.reachable_limit is None else "Insufficient energy — ride stopped",
                foreground="#b91c1c" if self.reachable_limit is not None or self.failure is not None else "#475569",
            )
            self._draw_track()
            self._draw_plots()
            self._update_live_readout()
            return

        self._draw_track()
        self._draw_plots()
        self._update_live_readout()
        self.animation_id = self.root.after(16, self._animate)


def main():
    root = tk.Tk()
    app = RollerCoasterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
