import tkinter as tk
from tkinter import ttk

from gui.register_view import RegisterView
from gui.profile_view import ProfileView
from gui.match_view import MatchView


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SteamTeam")
        self.root.geometry("980x620")
        self.root.minsize(900, 580)

        self._set_style()

        # Load logo (keep reference!)
        self.logo = tk.PhotoImage(file="assets/steamteam_logo_1.png")

        self.current_user = None

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
        self.card = "#171a21"
        self.text = "#ffffff"
        self.subtext = "#b8c0cc"
        self.active = "#1b1f2a"

        self.root.configure(bg=self.bg)

        style.configure(".", font=("Segoe UI", 11))

        # Base frames
        style.configure("TFrame", background=self.bg)
        style.configure("Card.TFrame", background=self.card)

        # Labels
        style.configure("Title.TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background=self.bg, foreground=self.subtext)

        style.configure("CardTitle.TLabel", background=self.card, foreground=self.text, font=("Segoe UI", 14, "bold"))
        style.configure("CardText.TLabel", background=self.card, foreground=self.subtext)

        # Image label in card
        style.configure("CardImg.TLabel", background=self.card)

        # Entry + buttons
        style.configure("TEntry", padding=8)

        style.configure("Primary.TButton", padding=10)
        style.map("Primary.TButton", background=[("active", "#3d66db")])

        # Sidebar buttons
        style.configure("Nav.TButton", padding=10, anchor="w")
        style.map("Nav.TButton", background=[("active", "#222633")])

        style.configure("NavActive.TButton", padding=10, anchor="w", background=self.active, foreground=self.text)

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
        ttk.Label(
            card,
            text="Enter a username or email to continue.",
            style="CardText.TLabel"
        ).pack(anchor="w", padx=18, pady=(0, 14))

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x", padx=18, pady=(0, 10))

        ttk.Label(form, text="Username or email", style="CardText.TLabel").pack(anchor="w", pady=(0, 6))
        self.username_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.username_var).pack(fill="x")

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.pack(fill="x", padx=18, pady=(0, 18))

        ttk.Button(
            actions,
            text="Login (soon)",
            style="Primary.TButton",
            command=self._enter_app_shell
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            actions,
            text="Register user",
            command=self._show_register
        ).pack(side="left")


    def _enter_app_shell(self):
        username = (self.username_var.get() or "").strip()
        self.current_user = username if username else "guest"
        self._build_app_shell()

    def _build_app_shell(self):
        for w in self.container.winfo_children():
            w.destroy()

        shell = ttk.Frame(self.container)
        shell.pack(fill="both", expand=True)

        # Topbar
        topbar = ttk.Frame(shell)
        topbar.pack(fill="x", padx=20, pady=(16, 10))

        ttk.Label(topbar, text="SteamTeam", style="Title.TLabel").pack(side="left")
        ttk.Label(topbar, text=f"User: {self.current_user}", style="Sub.TLabel").pack(side="right")

        body = ttk.Frame(shell)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Sidebar
        sidebar = ttk.Frame(body, style="Card.TFrame", width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="Navigation", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 10))

        self.nav_buttons = {}

        self.nav_buttons["profile"] = ttk.Button(
            sidebar,
            text="Profile",
            style="Nav.TButton",
            command=lambda: self._show_page("profile")
        )
        self.nav_buttons["profile"].pack(fill="x", padx=10, pady=4)

        self.nav_buttons["match"] = ttk.Button(
            sidebar,
            text="Match",
            style="Nav.TButton",
            command=lambda: self._show_page("match")
        )
        self.nav_buttons["match"].pack(fill="x", padx=10, pady=4)

        ttk.Separator(sidebar).pack(fill="x", padx=10, pady=12)
        ttk.Button(sidebar, text="Logout", style="Nav.TButton", command=self._logout).pack(fill="x", padx=10, pady=4)

        # Content (outer + inner för att den alltid ska synas tydligt)
        content_outer = ttk.Frame(body)
        content_outer.pack(side="right", fill="both", expand=True, padx=(16, 0))

        self.content = ttk.Frame(content_outer, style="Card.TFrame")
        self.content.pack(fill="both", expand=True, padx=14, pady=14)

        # Pages
        self.pages = {
            "profile": ProfileView(self.content),
            "match": MatchView(self.content),
        }
        self._show_page("profile")

    def _show_page(self, key: str):
        # Hide all pages
        for page in self.pages.values():
            page.hide()

        # Reset nav button styles
        for btn in self.nav_buttons.values():
            btn.configure(style="Nav.TButton")

        # Show selected page + mark active
        self.pages[key].show()
        self.nav_buttons[key].configure(style="NavActive.TButton")

    def _logout(self):
        self.current_user = None
        self._build_login_screen()

    def _show_register(self):
        for w in self.container.winfo_children():
            w.destroy()

        self.register_view = RegisterView(self.container, on_back=self._build_login_screen)
        self.register_view.show()
