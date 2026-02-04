from tkinter import ttk


class RegisterView:
    def __init__(self, parent, on_back):
        self.frame = ttk.Frame(parent, style="Card.TFrame")
        self.on_back = on_back

        ttk.Label(self.frame, text="Create user", style="CardTitle.TLabel").pack(
            anchor="w", padx=18, pady=(18, 6)
        )

        ttk.Label(
            self.frame,
            text="Register a new Steam profile (backend will be added later).",
            style="CardText.TLabel"
        ).pack(anchor="w", padx=18, pady=(0, 14))

        form = ttk.Frame(self.frame, style="Card.TFrame")
        form.pack(fill="x", padx=18, pady=(0, 10))

        self._field(form, "Username")
        self._field(form, "Email")
        self._field(form, "SteamID / Vanity / Profile URL")

        actions = ttk.Frame(self.frame, style="Card.TFrame")
        actions.pack(fill="x", padx=18, pady=(10, 18))

        ttk.Button(actions, text="Register account (soon)").pack(side="left", padx=(0, 10))
        ttk.Button(actions, text="Back", command=self.on_back).pack(side="left")

    def _field(self, parent, label):
        ttk.Label(parent, text=label, style="CardText.TLabel").pack(anchor="w", pady=(10, 4))
        ttk.Entry(parent).pack(fill="x")

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
