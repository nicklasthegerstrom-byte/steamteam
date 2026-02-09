import tkinter as tk
from tkinter import ttk


class MatchView:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="Card.TFrame")

        ttk.Label(self.frame, text="Matches", style="CardTitle.TLabel").pack(anchor="w", padx=18, pady=(18, 6))
        ttk.Label(
            self.frame,
            text="Find players that match your playstyle.",
            style="CardText.TLabel",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        controls = ttk.Frame(self.frame, style="Card.TFrame")
        controls.pack(fill="x", padx=18, pady=(0, 12))
        

        # MainWindow kopplar command senare via set_on_find
        self.find_btn = ttk.Button(controls, text="Find teammates")
        self.find_btn.pack(side="left")

        ttk.Separator(self.frame).pack(fill="x", padx=18, pady=14)

        # --- Scrollable results area ---
        outer = ttk.Frame(self.frame, style="Card.TFrame")
        outer.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.canvas = tk.Canvas(outer, highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.results = ttk.Frame(self.canvas, style="Card.TFrame")
        self.window_id = self.canvas.create_window((0, 0), window=self.results, anchor="nw")

        self.results.bind("<Configure>", self._on_results_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # mousewheel scroll (mac/windows)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel)

    def set_on_find(self, callback):
        self.find_btn.configure(command=callback)

    def set_results(self, cards):
        # clear
        for w in self.results.winfo_children():
            w.destroy()

        if not cards:
            ttk.Label(self.results, text="No matches found.", style="CardText.TLabel").pack(anchor="w", pady=10)
            return

        for card in cards:
            self._add_match_card(card)

    def _add_match_card(self, card):
        score_pct = int(round(float(card.score) * 100))
        score_exact = f"{float(card.score):.4f}"

        section = ttk.Frame(self.results, style="Card.TFrame")
        section.pack(fill="x", pady=(0, 18))

        # Header
        ttk.Label(section, text=f"{score_pct}% MATCH", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Separator(section).pack(fill="x", pady=(0, 10))

        # Identity
        ttk.Label(section, text=card.username, style="CardText.TLabel").pack(anchor="w")
        ttk.Label(section, text=f"Steam ID: {card.steam_id}", style="CardText.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Label(section, text=f"Score: {score_exact}", style="CardText.TLabel").pack(anchor="w", pady=(0, 10))

        grid = ttk.Frame(section, style="Card.TFrame")
        grid.pack(fill="x")

        left = ttk.Frame(grid, style="Card.TFrame")
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(grid, style="Card.TFrame")
        right.pack(side="right", fill="both", expand=True, padx=(24, 0))

        # Playstyle
        ttk.Label(left, text="Playstyle", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        for key in ["coop", "social", "pvp", "solo"]:
            pct = int(round(float(card.playstyles.get(key, 0.0)) * 100))
            ttk.Label(left, text=f"{key.capitalize():<7} {pct}%", style="CardText.TLabel").pack(anchor="w")

        ttk.Separator(left).pack(fill="x", pady=12)

        # Top Genres
        ttk.Label(left, text="Top Genres", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        for name, val in card.top_genres:
            pct = int(round(float(val) * 100))
            ttk.Label(left, text=f"{name:<12} {pct}%", style="CardText.TLabel").pack(anchor="w")

        # Top Games
        ttk.Label(right, text="Top Games", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        for name, hours in card.top_games:
            ttk.Label(right, text=f"{name}    {hours} h", style="CardText.TLabel").pack(anchor="w")

    def _on_results_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # keep inner frame width in sync with canvas width
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        # mac: event.delta is small; windows: larger
        delta = event.delta
        if delta == 0:
            return
        self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()


