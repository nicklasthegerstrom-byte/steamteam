from tkinter import ttk


class ProfileView:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="Card.TFrame")

        ttk.Label(self.frame, text="Profile", style="CardTitle.TLabel").pack(anchor="w", padx=18, pady=(18, 6))
        ttk.Label(
            self.frame,
            text="Manage your Steam profile (sync + export will be added later).",
            style="CardText.TLabel"
        ).pack(anchor="w", padx=18, pady=(0, 14))

        actions = ttk.Frame(self.frame, style="Card.TFrame")
        actions.pack(fill="x", padx=18, pady=(0, 18))

        ttk.Button(actions, text="Connect Steam (soon)").pack(side="left", padx=(0, 10))
        ttk.Button(actions, text="Update from Steam (soon)").pack(side="left", padx=(0, 10))
        ttk.Button(actions, text="Export JSON (soon)").pack(side="left")

        ttk.Separator(self.frame).pack(fill="x", padx=18, pady=14)

        ttk.Label(self.frame, text="Top games (preview)", style="CardTitle.TLabel").pack(
            anchor="w", padx=18, pady=(0, 8)
        )

        box = ttk.Frame(self.frame, style="Card.TFrame")
        box.pack(fill="x", padx=18, pady=(0, 18))

        for name in ["Game A", "Game B", "Game C", "Game D", "Game E"]:
            ttk.Label(box, text=f"• {name}", style="CardText.TLabel").pack(anchor="w", pady=2)

        ttk.Label(self.frame, text="Tags (preview)", style="CardTitle.TLabel").pack(
            anchor="w", padx=18, pady=(0, 8)
        )

        tags = ttk.Frame(self.frame, style="Card.TFrame")
        tags.pack(fill="x", padx=18, pady=(0, 18))

        ttk.Label(tags, text="Action • Co-op • Competitive • Strategy • RPG", style="CardText.TLabel").pack(anchor="w")

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()

