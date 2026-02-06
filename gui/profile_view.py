from tkinter import ttk
from services.profile_sync import sync_user_profile


class ProfileView:
    def __init__(self, parent, get_user_id_callback):
        self.frame = ttk.Frame(parent, style="Card.TFrame")
        self.get_user_id = get_user_id_callback

        ttk.Label(self.frame, text="Profile", style="CardTitle.TLabel").pack(
            anchor="w", padx=18, pady=(18, 6)
        )

        ttk.Label(
            self.frame,
            text="Manage your Steam profile and sync data.",
            style="CardText.TLabel",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        actions = ttk.Frame(self.frame, style="Card.TFrame")
        actions.pack(fill="x", padx=18, pady=(0, 10))

        ttk.Button(
            actions,
            text="Sync Profile",
            style="Primary.TButton",
            command=self._sync_profile,
        ).pack(side="left")

        self.status_var = ttk.Label(
            self.frame,
            text="",
            style="CardText.TLabel",
        )
        self.status_var.pack(anchor="w", padx=18, pady=(6, 12))

        ttk.Separator(self.frame).pack(fill="x", padx=18, pady=14)

        ttk.Label(
            self.frame,
            text="Top games (after sync)",
            style="CardTitle.TLabel",
        ).pack(anchor="w", padx=18, pady=(0, 8))

        self.preview_box = ttk.Frame(self.frame, style="Card.TFrame")
        self.preview_box.pack(fill="x", padx=18, pady=(0, 18))

    def _sync_profile(self):
        user_id = self.get_user_id()
        if not user_id:
            self.status_var.config(text="No user logged in.")
            return

        try:
            snapshot = sync_user_profile(user_id, top_n=5)
        except Exception as e:
            self.status_var.config(text=f"Sync failed: {e}")
            return

        self.status_var.config(text="Profile synced successfully.")

        for w in self.preview_box.winfo_children():
            w.destroy()

        for game in snapshot.top_games[:5]:
            name = game["name"]
            hours = round(game["playtime"] / 60)
            ttk.Label(
                self.preview_box,
                text=f"• {name} ({hours}h)",
                style="CardText.TLabel",
            ).pack(anchor="w", pady=2)

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
