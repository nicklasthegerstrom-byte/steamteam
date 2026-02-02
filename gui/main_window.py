import tkinter as tk
from tkinter import ttk


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SteamTeam")
        self.root.geometry("980x620")
        self.root.minsize(900, 580)

        self._set_style()

        # Load logo (keep reference!)
        self.logo = tk.PhotoImage(file="assets/steamteam_logo_1.png")

        # Root container
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Start on login screen (visual only)
        self._build_login_screen()

    def run(self):
        self.root.mainloop()

    def _set_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Base colors
        self.bg = "#0f1115"
        self.card = "#0f1115"
        self.text = "#ffffff"
        self.subtext = "#b8c0cc"

        self.root.configure(bg=self.bg)
        style.configure(".", font=("Segoe UI", 11))
        style.configure("TFrame", background=self.bg)
        style.configure("Card.TFrame", background=self.card)

        style.configure("Title.TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background=self.bg, foreground=self.subtext)

        style.configure("CardTitle.TLabel", background=self.card, foreground=self.text, font=("Segoe UI", 14, "bold"))
        style.configure("CardText.TLabel", background=self.card, foreground=self.subtext)

        style.configure("TEntry", padding=8)

        style.configure("Primary.TButton", padding=10)
        style.map("Primary.TButton", background=[("active", "#3d66db")])

        # Make sure image label matches card background
        style.configure("CardImg.TLabel", background=self.card)

    def _build_login_screen(self):
        for w in self.container.winfo_children():
            w.destroy()

        wrapper = ttk.Frame(self.container)
        wrapper.pack(fill="both", expand=True, padx=30, pady=30)

        ttk.Label(wrapper, text="SteamTeam", style="Title.TLabel").pack(anchor="w")

        card = ttk.Frame(wrapper, style="Card.TFrame")
        card.pack(anchor="center", fill="x", padx=140, pady=50)

        ttk.Label(card, image=self.logo, style="CardImg.TLabel").pack(pady=(18, 6))

        ttk.Label(card, text="Login", style="CardTitle.TLabel").pack(anchor="w", padx=18, pady=(16, 6))
        ttk.Label(card, text="Enter a username to continue.", style="CardText.TLabel").pack(
            anchor="w", padx=18, pady=(0, 14)
        )

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x", padx=18, pady=(0, 10))

        ttk.Label(form, text="Username", style="CardText.TLabel").pack(anchor="w", pady=(0, 6))
        self.username_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.username_var).pack(fill="x")

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.pack(fill="x", padx=18, pady=(0, 18))

        ttk.Button(actions, text="Login (soon)", style="Primary.TButton", command=lambda: None).pack(
            side="left", padx=(0, 10)
        )
        ttk.Button(actions, text="Create user (soon)", command=lambda: None).pack(side="left")
