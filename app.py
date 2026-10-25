import os
import tkinter as tk
from tkinter import ttk, messagebox
from src.graph import RailwayGraph
from src.algorithms import bfs_min_stops, dijkstra_shortest_path

# Modern Dark Theme Color Palette (Tailwind Slate & Indigo inspired)
BG_MAIN = "#0f172a"       # Deep Slate background
BG_CARD = "#1e293b"       # Elevated card surface
BG_INPUT = "#334155"      # Dropdown/input background
FG_TEXT = "#f8fafc"       # Crisp white text
FG_MUTED = "#94a3b8"      # Muted silver-grey text
ACCENT_PRIMARY = "#6366f1"# Indigo primary button
ACCENT_HOVER = "#4f46e5"  # Indigo hover
ACCENT_CYAN = "#06b6d4"   # Neon Cyan for active route
ACCENT_GREEN = "#10b981"  # Emerald green for optimal badges
ACCENT_AMBER = "#f59e0b"  # Amber for warnings/stops
EDGE_DEFAULT = "#475569"  # Unvisited track color

# Normalized (x, y) coordinates (0.0 to 1.0) for visual map layout of Indian Junctions
STATION_COORDS = {
    "NDLS": (0.52, 0.12),  # New Delhi (North)
    "JP":   (0.38, 0.24),  # Jaipur
    "KOTA": (0.45, 0.36),  # Kota
    "ADI":  (0.18, 0.44),  # Ahmedabad (West)
    "RTM":  (0.36, 0.48),  # Ratlam
    "BPL":  (0.54, 0.50),  # Bhopal (Central)
    "BRC":  (0.22, 0.56),  # Vadodara
    "ST":   (0.20, 0.68),  # Surat
    "NGP":  (0.64, 0.64),  # Nagpur
    "MMCT": (0.16, 0.80),  # Mumbai Central
    "PUNE": (0.28, 0.85),  # Pune
    "SC":   (0.58, 0.88),  # Secunderabad (South)
}


class ModernRailwayApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🚆 Railway Route Finder & DAA Visualizer")
        self.root.geometry("1220x760")
        self.root.minsize(1050, 680)
        self.root.configure(bg=BG_MAIN)

        data_path = os.path.join(os.path.dirname(__file__), "data", "stations.json")
        self.graph = RailwayGraph.load_from_json(data_path)
        self.station_codes = sorted(self.graph.stations.keys())
        self.station_display = [
            f"{code} — {self.graph.stations[code]['name']}"
            for code in self.station_codes
        ]

        self.active_path = []
        self._configure_styles()
        self._build_layout()
        self.root.after(100, self.run_analysis)  # Auto-run initial demo on startup

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        # Modern Combobox styling
        style.configure(
            "TCombobox",
            fieldbackground=BG_INPUT,
            background=BG_INPUT,
            foreground=FG_TEXT,
            arrowcolor=FG_TEXT,
            borderwidth=0,
            padding=6
        )
        self.root.option_add("*TCombobox*Listbox*Background", BG_CARD)
        self.root.option_add("*TCombobox*Listbox*Foreground", FG_TEXT)
        self.root.option_add("*TCombobox*Listbox*selectBackground", ACCENT_PRIMARY)

        # Modern Dark Treeview (Table) styling
        style.configure(
            "Dark.Treeview",
            background=BG_CARD,
            foreground=FG_TEXT,
            fieldbackground=BG_CARD,
            rowheight=32,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Dark.Treeview.Heading",
            background="#0f172a",
            foreground=ACCENT_CYAN,
            font=("Segoe UI", 10, "bold"),
            padding=8,
            borderwidth=0
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", ACCENT_PRIMARY)],
            foreground=[("selected", "#ffffff")]
        )

    def _build_layout(self) -> None:
        # 1. Top Navigation Header
        header = tk.Frame(self.root, bg="#090d16", padx=24, pady=14)
        header.pack(fill="x")

        title_box = tk.Frame(header, bg="#090d16")
        title_box.pack(side="left")
        tk.Label(
            title_box,
            text="🚆 RAILWAY ROUTE FINDER",
            font=("Segoe UI", 16, "bold"),
            fg=FG_TEXT,
            bg="#090d16"
        ).pack(side="left")
        tk.Label(
            title_box,
            text="  |  DAA GRAPH & SHORTEST PATH VISUALIZER",
            font=("Segoe UI", 11, "bold"),
            fg=ACCENT_CYAN,
            bg="#090d16"
        ).pack(side="left", pady=(2, 0))

        badge = tk.Label(
            header,
            text=f" Graph G(V={len(self.graph.stations)}, E={self.graph.num_edges}) • Adjacency List O(V+E) ",
            font=("Consolas", 9, "bold"),
            fg=ACCENT_GREEN,
            bg="#132a2e",
            padx=10,
            pady=4
        )
        badge.pack(side="right")

        # 2. Main Split Workspace (Left Sidebar + Right Dashboard)
        workspace = tk.Frame(self.root, bg=BG_MAIN, padx=18, pady=14)
        workspace.pack(fill="both", expand=True)

        # --- LEFT SIDEBAR (CONTROLS) ---
        sidebar = tk.Frame(workspace, bg=BG_CARD, width=320, padx=18, pady=18)
        sidebar.pack(side="left", fill="y", padx=(0, 14))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="ROUTE CONFIGURATION",
            font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg=BG_CARD
        ).pack(anchor="w", pady=(0, 12))

        # Source Selector
        tk.Label(sidebar, text="Origin Station (Source)", font=("Segoe UI", 9, "bold"), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w")
        self.src_combo = ttk.Combobox(sidebar, values=self.station_display, state="readonly", font=("Segoe UI", 10))
        self.src_combo.current(self.station_codes.index("ST") if "ST" in self.station_codes else 0)
        self.src_combo.pack(fill="x", pady=(4, 14))

        # Destination Selector
        tk.Label(sidebar, text="Destination Station (Target)", font=("Segoe UI", 9, "bold"), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w")
        self.dst_combo = ttk.Combobox(sidebar, values=self.station_display, state="readonly", font=("Segoe UI", 10))
        self.dst_combo.current(self.station_codes.index("NDLS") if "NDLS" in self.station_codes else 1)
        self.dst_combo.pack(fill="x", pady=(4, 18))

        # Algorithm Mode Selector
        tk.Label(
            sidebar, text="ALGORITHM / OPTIMIZATION",
            font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg=BG_CARD
        ).pack(anchor="w", pady=(4, 8))

        self.algo_var = tk.StringVar(value="compare")
        modes = [
            ("⚡ Compare All (DAA Benchmark)", "compare"),
            ("🛑 Minimum Stops (BFS Traversal)", "bfs"),
            ("📏 Shortest Distance (Dijkstra)", "distance"),
            ("⏱️ Fastest Travel Time (Dijkstra)", "time"),
            ("₹  Cheapest Ticket Fare (Dijkstra)", "cost"),
        ]

        for label, val in modes:
            rb = tk.Radiobutton(
                sidebar, text=label, variable=self.algo_var, value=val,
                font=("Segoe UI", 10), fg=FG_TEXT, bg=BG_CARD,
                selectcolor=BG_INPUT, activebackground=BG_CARD,
                activeforeground=ACCENT_CYAN, cursor="hand2", anchor="w", pady=4,
                command=self.run_analysis
            )
            rb.pack(fill="x")

        # Compute CTA Button
        compute_btn = tk.Button(
            sidebar,
            text="COMPUTE OPTIMAL ROUTE",
            command=self.run_analysis,
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_PRIMARY,
            fg="#ffffff",
            activebackground=ACCENT_HOVER,
            activeforeground="#ffffff",
            relief="flat",
            pady=10,
            cursor="hand2"
        )
        compute_btn.pack(fill="x", pady=(22, 10))

        # Legend Box inside Sidebar
        legend = tk.Frame(sidebar, bg="#162032", padx=12, pady=10)
        legend.pack(fill="x", side="bottom")
        tk.Label(legend, text="MAP LEGEND", font=("Segoe UI", 8, "bold"), fg=FG_MUTED, bg="#162032").pack(anchor="w")
        tk.Label(legend, text="● Cyan Glow : Optimal Active Route", font=("Segoe UI", 9), fg=ACCENT_CYAN, bg="#162032").pack(anchor="w", pady=2)
        tk.Label(legend, text="● Green Node: Origin / Destination", font=("Segoe UI", 9), fg=ACCENT_GREEN, bg="#162032").pack(anchor="w", pady=2)
        tk.Label(legend, text="● Slate Line: Available Railway Track", font=("Segoe UI", 9), fg=FG_MUTED, bg="#162032").pack(anchor="w", pady=2)

        # --- RIGHT AREA (KPI CARDS + MAP CANVAS + TABLE) ---
        right_panel = tk.Frame(workspace, bg=BG_MAIN)
        right_panel.pack(side="left", fill="both", expand=True)

        # KPI Metric Cards Row
        kpi_row = tk.Frame(right_panel, bg=BG_MAIN)
        kpi_row.pack(fill="x", pady=(0, 12))

        self.kpi_cards = {}
        kpi_specs = [
            ("route", "OPTIMAL ROUTE PATH", ACCENT_CYAN),
            ("metrics", "DISTANCE  •  TIME  •  FARE", ACCENT_GREEN),
            ("daa", "DAA COMPLEXITY & NODES", ACCENT_AMBER),
        ]
        for key, title, color in kpi_specs:
            card = tk.Frame(kpi_row, bg=BG_CARD, padx=16, pady=12)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10 if key != "daa" else 0))
            tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w")
            val_lbl = tk.Label(card, text="—", font=("Segoe UI", 11, "bold"), fg=color, bg=BG_CARD, justify="left")
            val_lbl.pack(anchor="w", pady=(4, 0))
            self.kpi_cards[key] = val_lbl

        # Interactive Network Map Canvas
        map_frame = tk.Frame(right_panel, bg=BG_CARD, padx=2, pady=2)
        map_frame.pack(fill="both", expand=True, pady=(0, 12))

        self.canvas = tk.Canvas(map_frame, bg="#0b1120", highlightthickness=0, height=280)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw_network_map())

        # Bottom Data Table
        table_container = tk.Frame(right_panel, bg=BG_CARD, padx=12, pady=10)
        table_container.pack(fill="x")

        self.table_title = tk.Label(
            table_container,
            text="DAA ALGORITHMIC BENCHMARK TABLE",
            font=("Segoe UI", 9, "bold"),
            fg=FG_MUTED,
            bg=BG_CARD
        )
        self.table_title.pack(anchor="w", pady=(0, 6))

        self.tree = ttk.Treeview(table_container, style="Dark.Treeview", show="headings", height=5)
        self.tree.pack(fill="x")

    def _format_time(self, mins: int) -> str:
        return f"{mins // 60}h {mins % 60}m"

    def _draw_network_map(self) -> None:
        """Draws all railway tracks, stations, and highlights the active optimal route."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            return

        # Convert normalized coords to canvas pixel coordinates
        px_coords = {
            code: (int(x * (w - 90) + 45), int(y * (h - 60) + 30))
            for code, (x, y) in STATION_COORDS.items()
            if code in self.graph.stations
        }

        # Determine active edges set
        active_edges = set()
        for i in range(len(self.active_path) - 1):
            u, v = self.active_path[i], self.active_path[i + 1]
            active_edges.add((u, v))
            active_edges.add((v, u))

        # 1. Draw all background railway tracks
        drawn_pairs = set()
        for u, neighbors in self.graph.adj_list.items():
            for n in neighbors:
                v = n["station"]
                if (v, u) in drawn_pairs or u not in px_coords or v not in px_coords:
                    continue
                drawn_pairs.add((u, v))
                x1, y1 = px_coords[u]
                x2, y2 = px_coords[v]

                is_active = (u, v) in active_edges
                color = ACCENT_CYAN if is_active else EDGE_DEFAULT
                width = 4 if is_active else 1.5

                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

                # Draw distance label on midpoint
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                lbl_color = "#ffffff" if is_active else "#64748b"
                self.canvas.create_text(
                    mx, my - 7,
                    text=f"{n['distance']}km",
                    fill=lbl_color,
                    font=("Segoe UI", 8, "bold" if is_active else "normal")
                )

        # 2. Draw station nodes
        for code, (x, y) in px_coords.items():
            in_path = code in self.active_path
            is_endpoint = len(self.active_path) >= 2 and code in (self.active_path[0], self.active_path[-1])

            if is_endpoint:
                r = 10
                fill_col = ACCENT_GREEN
                outline_col = "#ffffff"
            elif in_path:
                r = 9
                fill_col = ACCENT_CYAN
                outline_col = "#ffffff"
            else:
                r = 6
                fill_col = BG_CARD
                outline_col = "#94a3b8"

            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=fill_col, outline=outline_col, width=2
            )
            self.canvas.create_text(
                x, y - r - 10,
                text=f"{code}",
                fill="#ffffff" if in_path else "#cbd5e1",
                font=("Segoe UI", 9, "bold")
            )

    def run_analysis(self) -> None:
        src = self.station_codes[self.src_combo.current()]
        dst = self.station_codes[self.dst_combo.current()]

        if src == dst:
            messagebox.showwarning("Same Station", "Please select different Origin and Destination stations.")
            return

        mode = self.algo_var.get()
        for item in self.tree.get_children():
            self.tree.delete(item)

        if mode == "compare":
            results = [
                bfs_min_stops(self.graph, src, dst),
                dijkstra_shortest_path(self.graph, src, dst, "distance"),
                dijkstra_shortest_path(self.graph, src, dst, "time"),
                dijkstra_shortest_path(self.graph, src, dst, "cost"),
            ]
            # Highlight Dijkstra Shortest Distance on the canvas by default in benchmark mode
            best_dist = results[1]
            self.active_path = best_dist["path"]
            self._draw_network_map()

            self.kpi_cards["route"].config(text=" ➔ ".join(best_dist["path"]) + "  (Dijkstra)")
            self.kpi_cards["metrics"].config(
                text=f"{best_dist['total_distance']} km   •   {self._format_time(best_dist['total_time'])}   •   ₹{best_dist['total_cost']}"
            )
            self.kpi_cards["daa"].config(
                text=f"BFS: {results[0]['stops']} stops ({results[0]['total_distance']} km)  vs  Dijkstra: {best_dist['stops']} stops ({best_dist['total_distance']} km)"
            )

            self.table_title.config(text=f"SIDE-BY-SIDE DAA BENCHMARK COMPARISON ({src} ➔ {dst})")
            cols = ("Algorithm", "Optimal Path", "Stops", "Distance", "Travel Time", "Fare", "Nodes Visited", "Exec Time", "Time Complexity")
            self.tree["columns"] = cols
            widths = [200, 210, 60, 85, 85, 75, 95, 85, 120]
            for col, w in zip(cols, widths):
                self.tree.heading(col, text=col)
                self.tree.column(col, width=w, anchor="center")

            for res in results:
                self.tree.insert("", "end", values=(
                    res["algorithm"],
                    " ➔ ".join(res["path"]),
                    res["stops"],
                    f"{res['total_distance']} km",
                    self._format_time(res["total_time"]),
                    f"₹{res['total_cost']}",
                    f"{res['nodes_visited']}/{len(self.graph.stations)}",
                    f"{res['execution_time_ms']} ms",
                    res["time_complexity"]
                ))
        else:
            res = bfs_min_stops(self.graph, src, dst) if mode == "bfs" else dijkstra_shortest_path(self.graph, src, dst, mode)
            self.active_path = res["path"]
            self._draw_network_map()

            self.kpi_cards["route"].config(text=" ➔ ".join(res["path"]))
            self.kpi_cards["metrics"].config(
                text=f"{res['total_distance']} km   •   {self._format_time(res['total_time'])}   •   ₹{res['total_cost']}   ({res['stops']} stops)"
            )
            self.kpi_cards["daa"].config(
                text=f"{res['time_complexity']}  •  {res['nodes_visited']}/{len(self.graph.stations)} Nodes  •  {res['execution_time_ms']} ms"
            )

            self.table_title.config(text=f"STEP-BY-STEP TRACK BREAKDOWN — {res['algorithm'].upper()}")
            cols = ("Step", "From Junction", "To Junction", "Track Distance", "Duration", "Ticket Cost")
            self.tree["columns"] = cols
            widths = [70, 230, 230, 130, 130, 130]
            for col, w in zip(cols, widths):
                self.tree.heading(col, text=col)
                self.tree.column(col, width=w, anchor="center")

            for idx, seg in enumerate(res["segments"], start=1):
                self.tree.insert("", "end", values=(
                    f"Hop {idx}",
                    self.graph.get_station_name(seg["from"]),
                    self.graph.get_station_name(seg["to"]),
                    f"{seg['distance']} km",
                    self._format_time(seg["time"]),
                    f"₹{seg['cost']}"
                ))


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernRailwayApp(root)
    root.mainloop()