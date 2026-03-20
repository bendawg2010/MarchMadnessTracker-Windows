"""Main popup window with Scores / Bracket / Schedule tabs."""

import tkinter as tk
import tkinter.ttk as ttk
from ui.styles import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, FONT_TITLE, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL,
    MAIN_WIDTH, MAIN_HEIGHT,
    apply_dark_theme,
)
from ui.scores_tab import ScoresTab
from ui.bracket_tab import BracketTab
from ui.schedule_tab import ScheduleTab


class MainWindow(tk.Toplevel):
    """Primary application window with tabbed interface."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.title("March Madness Tracker")
        self.configure(bg=BG_PRIMARY)
        self.geometry(f"{MAIN_WIDTH}x{MAIN_HEIGHT}")
        self.minsize(420, 480)

        apply_dark_theme(self)

        # ── Header ─────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG_PRIMARY, padx=12, pady=8)
        header.pack(fill="x")

        title_frame = tk.Frame(header, bg=BG_PRIMARY)
        title_frame.pack(side="left")

        tk.Label(title_frame, text="\U0001f3c0", bg=BG_PRIMARY,
                 font=("Segoe UI Emoji", 20)).pack(side="left", padx=(0, 8))
        tk.Label(title_frame, text="March Madness", bg=BG_PRIMARY,
                 fg=TEXT_PRIMARY, font=FONT_TITLE).pack(side="left")

        # Header buttons
        btn_frame = tk.Frame(header, bg=BG_PRIMARY)
        btn_frame.pack(side="right")

        ticker_btn = tk.Button(
            btn_frame, text="\u2261 Ticker", bg=BG_TERTIARY, fg=TEXT_PRIMARY,
            font=FONT_SMALL, bd=0, padx=8, pady=3, cursor="hand2",
            activebackground=ACCENT, activeforeground="white",
            command=self.app.toggle_ticker,
        )
        ticker_btn.pack(side="left", padx=3)

        settings_btn = tk.Button(
            btn_frame, text="\u2699 Settings", bg=BG_TERTIARY, fg=TEXT_PRIMARY,
            font=FONT_SMALL, bd=0, padx=8, pady=3, cursor="hand2",
            activebackground=ACCENT, activeforeground="white",
            command=self.app.open_settings,
        )
        settings_btn.pack(side="left", padx=3)

        # ── Status bar ────────────────────────────────────────────────────
        self._status_frame = tk.Frame(self, bg=BG_SECONDARY, height=24)
        self._status_frame.pack(fill="x")
        self._status_frame.pack_propagate(False)

        self._status_dot = tk.Label(self._status_frame, text="\u25cf",
                                    bg=BG_SECONDARY, fg=TEXT_SECONDARY,
                                    font=FONT_SMALL)
        self._status_dot.pack(side="left", padx=(8, 4))
        self._status_label = tk.Label(self._status_frame, text="Connecting...",
                                      bg=BG_SECONDARY, fg=TEXT_SECONDARY,
                                      font=FONT_SMALL)
        self._status_label.pack(side="left")

        self._game_count_label = tk.Label(self._status_frame, text="",
                                          bg=BG_SECONDARY, fg=TEXT_SECONDARY,
                                          font=FONT_SMALL)
        self._game_count_label.pack(side="right", padx=8)

        # ── Notebook (tabs) ────────────────────────────────────────────────
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True, padx=4, pady=(4, 0))

        self.scores_tab = ScoresTab(self._notebook, app)
        self.bracket_tab = BracketTab(self._notebook, app)
        self.schedule_tab = ScheduleTab(self._notebook, app)

        self._notebook.add(self.scores_tab, text="  Scores  ")
        self._notebook.add(self.bracket_tab, text="  Bracket  ")
        self._notebook.add(self.schedule_tab, text="  Schedule  ")

        # ── Bottom bar ─────────────────────────────────────────────────────
        bottom = tk.Frame(self, bg=BG_PRIMARY, pady=6)
        bottom.pack(fill="x")

        quit_btn = tk.Button(
            bottom, text="Quit", bg=ACCENT, fg="white",
            font=FONT_BODY_BOLD, bd=0, padx=16, pady=4, cursor="hand2",
            activebackground="#c0392b", activeforeground="white",
            command=self.app.quit_app,
        )
        quit_btn.pack(side="right", padx=12)

        refresh_btn = tk.Button(
            bottom, text="\u21bb Refresh Bracket", bg=BG_TERTIARY,
            fg=TEXT_PRIMARY, font=FONT_SMALL, bd=0, padx=10, pady=4,
            cursor="hand2", activebackground=ACCENT,
            activeforeground="white",
            command=self.bracket_tab.refresh,
        )
        refresh_btn.pack(side="right", padx=4)

        # Handle window close -> hide instead of destroy
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """Hide window instead of destroying it."""
        self.withdraw()

    def update_status(self, games):
        """Update the status bar based on current games."""
        live_count = sum(1 for g in games if g.is_live)
        total = len(games)

        if live_count > 0:
            self._status_dot.configure(fg="#00e676")
            self._status_label.configure(
                text=f"{live_count} live game{'s' if live_count != 1 else ''}",
                fg="#00e676")
        elif total > 0:
            self._status_dot.configure(fg=TEXT_SECONDARY)
            self._status_label.configure(text="No live games", fg=TEXT_SECONDARY)
        else:
            self._status_dot.configure(fg=TEXT_SECONDARY)
            self._status_label.configure(text="No games today", fg=TEXT_SECONDARY)

        self._game_count_label.configure(text=f"{total} games")

    def show(self):
        """Show and bring to front."""
        self.deiconify()
        self.lift()
        self.focus_force()
