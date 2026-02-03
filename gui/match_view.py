import tkinter as tk
from tkinter import ttk


class MatchView:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="Card.TFrame")

        ttk.Label(self.frame, text="Match", style="CardTitle.TLabel").pack(anchor="w", padx=18, pady=(18, 6))
        ttk.Label(
            self.frame,
            text="Choose match mode and view results (logic will be added later).",
            style="CardText.TLabel"
        ).pack(anchor="w", padx=18, pady=(0, 14))

        controls = ttk.Frame(self.frame, style="Card.TFrame")
        controls.pack(fill="x", padx=18, pady=(0, 12))

        ttk.Label(controls, text="Mode", style="CardText.TLabel").pack(side="left", padx=(0, 10))

        self.mode_var = tk.StringVar(value="Games")
        ttk.Combobox(
            controls,
            textvariable=self.mode_var,
            values=["Games", "Tags", "Playstyle"],
            state="readonly",
            width=14
        ).pack(side="left", padx=(0, 12))

        ttk.Button(controls, text="Find teammates (soon)").pack(side="left")

        ttk.Separator(self.frame).pack(fill="x", padx=18, pady=14)

        ttk.Label(self.frame, text="Results (preview)", style="CardTitle.TLabel").pack(
            anchor="w", padx=18, pady=(0, 8)
        )

        results = ttk.Frame(self.frame, style="Card.TFrame")
        results.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        for row in [
            ("PlayerOne", "92%"),
            ("PlayerTwo", "88%"),
            ("PlayerThree", "84%"),
            ("PlayerFour", "79%"),
        ]:
            line = ttk.Frame(results, style="Card.TFrame")
            line.pack(fill="x", pady=6)

            ttk.Label(line, text=row[0], style="CardText.TLabel").pack(side="left")
            ttk.Label(line, text=row[1], style="CardText.TLabel").pack(side="right")

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()

