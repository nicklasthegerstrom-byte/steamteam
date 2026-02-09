import tkinter as tk
from tkinter import ttk

from services.auth_service import login
from services.matching_service import match_user_id
from gui.register_view import RegisterView
from gui.profile_view import ProfileView
from gui.match_view import MatchView

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *, style="TFrame"):
        super().__init__(parent, style=style)

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = ttk.Frame(self.canvas, style=style)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel (macOS + Windows/Linux)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)      # Win/mac
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)  # Linux up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)  # Linux down

    def _on_frame_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        # macOS: event.delta is small, Windows: 120 steps
        delta = event.delta
        if delta == 0:
            return
        step = -1 if delta > 0 else 1
        self.canvas.yview_scroll(step, "units")

    def _on_mousewheel_linux(self, event):
        step = -1 if event.num == 4 else 1
        self.canvas.yview_scroll(step, "units")


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
        self.current_user_id = None

        # Root container
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Start on login screen
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

        style.configure("TFrame", background=self.bg)
        style.configure("Card.TFrame", background=self.card)

        style.configure("Title.TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background=self.bg, foreground=self.subtext)

        style.configure("CardTitle.TLabel", background=self.card, foreground=self.text, font=("Segoe UI", 14, "bold"))
        style.configure("CardText.TLabel", background=self.card, foreground=self.subtext)

        style.configure("CardImg.TLabel", background=self.card)

        style.configure("TEntry", padding=8)

        style.configure("Primary.TButton", padding=10)
        style.map("Primary.TButton", background=[("active", "#3d66db")])

        style.configure("Nav.TButton", padding=10, anchor="w")
        style.map("Nav.TButton", background=[("active", "#222633")])

        style.configure("NavActive.TButton", padding=10, anchor="w", background=self.active, foreground=self.text)

    def _build_login_screen(self):
        for w in self.container.winfo_children():
            w.destroy()

        wrapper_sf = ScrollableFrame(self.container, style="TFrame")
        wrapper_sf.pack(fill="both", expand=True)

        wrapper = wrapper_sf.inner
        wrapper.configure(padding=(30, 30))


        ttk.Label(wrapper, text="SteamTeam", style="Title.TLabel").pack(anchor="w")

        card = ttk.Frame(wrapper, style="Card.TFrame")
        card.pack(anchor="center", fill="x", padx=140, pady=50)

        ttk.Label(card, image=self.logo, style="CardImg.TLabel").pack(pady=(18, 6))

        ttk.Label(card, text="Login", style="CardTitle.TLabel").pack(anchor="w", padx=18, pady=(16, 6))
        ttk.Label(
            card,
            text="Enter a username or email to continue.",
            style="CardText.TLabel",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x", padx=18, pady=(0, 10))

        ttk.Label(form, text="Username or email", style="CardText.TLabel").pack(anchor="w", pady=(0, 6))
        self.username_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.username_var).pack(fill="x")

        self.login_error_var = tk.StringVar(value="")
        ttk.Label(form, textvariable=self.login_error_var, style="CardText.TLabel").pack(anchor="w", pady=(8, 0))

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.pack(fill="x", padx=18, pady=(0, 18))

        ttk.Button(
            actions,
            text="Login",
            style="Primary.TButton",
            command=self._enter_app_shell,
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            actions,
            text="Register user",
            command=self._show_register,
        ).pack(side="left")

    def _enter_app_shell(self):
        identifier = (self.username_var.get() or "").strip()
        self.login_error_var.set("")

        if not identifier:
            self.login_error_var.set("Enter a username or email.")
            return

        try:
            user = login(identifier)
        except Exception as e:
            self.login_error_var.set(str(e))
            return

        if not user:
            self.login_error_var.set("User not found. Please register.")
            return

        self.current_user_id = user["user_id"]
        self.current_user = user["username"]
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
            command=lambda: self._show_page("profile"),
        )
        self.nav_buttons["profile"].pack(fill="x", padx=10, pady=4)

        self.nav_buttons["match"] = ttk.Button(
            sidebar,
            text="Match",
            style="Nav.TButton",
            command=lambda: self._show_page("match"),
        )
        self.nav_buttons["match"].pack(fill="x", padx=10, pady=4)

        ttk.Separator(sidebar).pack(fill="x", padx=10, pady=12)
        ttk.Button(sidebar, text="Logout", style="Nav.TButton", command=self._logout).pack(fill="x", padx=10, pady=4)

        # Content
        content_outer = ttk.Frame(body)
        content_outer.pack(side="right", fill="both", expand=True, padx=(16, 0))

        self.content = ttk.Frame(content_outer, style="Card.TFrame")
        self.content.pack(fill="both", expand=True, padx=14, pady=14)

        # Pages
        self.pages = {
            "profile": ProfileView(self.content, get_user_id_callback=lambda: self.current_user_id),
            "match": MatchView(self.content),
        }


        self._show_page("profile")

    def _run_matching(self):
        if self.current_user_id is None:
            return
        cards = match_user_id(self.current_user_id, top_n=5)
        self.pages["match"].set_results(cards)

    def _show_page(self, key: str):
        for page in self.pages.values():
            page.hide()

        for btn in self.nav_buttons.values():
            btn.configure(style="Nav.TButton")

        self.pages[key].show()
        self.nav_buttons[key].configure(style="NavActive.TButton")

        if key == "match":
            self._run_matching()

    def _logout(self):
        self.current_user = None
        self.current_user_id = None
        self._build_login_screen()

    def _show_register(self):
        for w in self.container.winfo_children():
            w.destroy()

        self.register_view = RegisterView(
            self.container,
            on_back=self._build_login_screen,
            on_created=self._on_register_success,
        )
        self.register_view.show()

    def _on_register_success(self, user_id: int, username: str):
        self.current_user_id = user_id
        self.current_user = username
        self._build_app_shell()


if __name__ == "__main__":
    MainWindow().run()
