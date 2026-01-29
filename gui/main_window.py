import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SteamTeam")
        self.root.geometry("900x600")

        label = ttk.Label(
            self.root,
            text="SteamTeam - GUI skeleton",
            font=("Segoe UI", 20)
        )
        label.pack(expand=True)

    def run(self):
        self.root.mainloop()
