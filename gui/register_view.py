import tkinter as tk
from tkinter import ttk

from services.auth_service import signup


class RegisterView:
    def __init__(self, parent, on_back, on_created):
        self.frame = ttk.Frame(parent, style="Card.TFrame")
        self.on_back = on_back
        self.on_created = on_created

        ttk.Label(self.frame, text="Create user", style="CardTitle.TLabel").pack(
            anchor="w", padx=18, pady=(18, 6)
        )

        ttk.Label(
            self.frame,
            text="Register a new Steam profile.",
            style="CardText.TLabel",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        form = ttk.Frame(self.frame, style="Card.TFrame")
        form.pack(fill="x", padx=18, pady=(0, 10))

        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.steam_var = tk.StringVar()

        self._field(form, "Username", self.username_var)
        self._field(form, "Email", self.email_var)
        self._field(form, "SteamID / Vanity / Profile URL", self.steam_var)

        self.error_var = tk.StringVar(value="")
        ttk.Label(form, textvariable=self.error_var, style="CardText.TLabel").pack(anchor="w", pady=(10, 0))

        actions = ttk.Frame(self.frame, style="Card.TFrame")
        actions.pack(fill="x", padx=18, pady=(10, 18))

        ttk.Button(actions, text="Create account", style="Primary.TButton", command=self._create_account).pack(
            side="left", padx=(0, 10)
        )
        ttk.Button(actions, text="Back", command=self.on_back).pack(side="left")

    def _field(self, parent, label, var: tk.StringVar):
        ttk.Label(parent, text=label, style="CardText.TLabel").pack(anchor="w", pady=(10, 4))
        ttk.Entry(parent, textvariable=var).pack(fill="x")

    def _create_account(self):
        self.error_var.set("")

        username = (self.username_var.get() or "").strip()
        email = (self.email_var.get() or "").strip()
        steam_id = (self.steam_var.get() or "").strip()

        if not username or not email or not steam_id:
            self.error_var.set("Please fill in username, email, and Steam ID/URL.")
            return

        try:
            user_id = signup(username=username, email=email, steam_id=steam_id)
        except Exception as e:
            self.error_var.set(str(e))
            return

        self.on_created(user_id, username)

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
