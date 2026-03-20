"""Floating always-on-top score widget for a single game."""

import tkinter as tk
from ui.styles import (
    BG_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    LIVE_GREEN, UPSET_GOLD, ACCENT, BORDER,
    FONT_BODY, FONT_BODY_BOLD, FONT_SCORE, FONT_SMALL, FONT_SEED,
    WIDGET_WIDTH, WIDGET_HEIGHT,
)
from espn_api import Game


class ScoreWidget(tk.Toplevel):
    """Small floating window showing a single game's live score."""

    def __init__(self, master, game: Game):
        super().__init__(master)
        self.game_id = game.id
        self.title(game.short_name or "Game")
        self.configure(bg=BG_SECONDARY)
        self.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.overrideredirect(False)

        # Try to remove title bar on Windows for sleek look
        try:
            self.attributes("-toolwindow", True)
        except Exception:
            pass

        self._drag_data = {"x": 0, "y": 0}
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)

        # Close button
        close_btn = tk.Button(self, text="\u2715", bg=BG_SECONDARY, fg=TEXT_DIM,
                              font=FONT_SMALL, bd=0, cursor="hand2",
                              activebackground=ACCENT, activeforeground="white",
                              command=self.destroy)
        close_btn.place(relx=1.0, x=-4, y=4, anchor="ne")

        # Content
        self._content = tk.Frame(self, bg=BG_SECONDARY)
        self._content.pack(fill="both", expand=True, padx=8, pady=6)

        # Away row
        self._away_frame = tk.Frame(self._content, bg=BG_SECONDARY)
        self._away_frame.pack(fill="x", pady=2)
        self._away_seed = tk.Label(self._away_frame, text="", bg=BG_SECONDARY,
                                   fg=TEXT_DIM, font=FONT_SEED, width=4, anchor="e")
        self._away_seed.pack(side="left")
        self._away_color = tk.Frame(self._away_frame, bg="#333", width=3, height=16)
        self._away_color.pack(side="left", padx=(4, 6))
        self._away_name = tk.Label(self._away_frame, text="", bg=BG_SECONDARY,
                                   fg=TEXT_PRIMARY, font=FONT_BODY_BOLD, anchor="w")
        self._away_name.pack(side="left", expand=True, fill="x")
        self._away_score = tk.Label(self._away_frame, text="", bg=BG_SECONDARY,
                                    fg=TEXT_PRIMARY, font=FONT_SCORE, anchor="e")
        self._away_score.pack(side="right")

        # Home row
        self._home_frame = tk.Frame(self._content, bg=BG_SECONDARY)
        self._home_frame.pack(fill="x", pady=2)
        self._home_seed = tk.Label(self._home_frame, text="", bg=BG_SECONDARY,
                                   fg=TEXT_DIM, font=FONT_SEED, width=4, anchor="e")
        self._home_seed.pack(side="left")
        self._home_color = tk.Frame(self._home_frame, bg="#333", width=3, height=16)
        self._home_color.pack(side="left", padx=(4, 6))
        self._home_name = tk.Label(self._home_frame, text="", bg=BG_SECONDARY,
                                   fg=TEXT_PRIMARY, font=FONT_BODY_BOLD, anchor="w")
        self._home_name.pack(side="left", expand=True, fill="x")
        self._home_score = tk.Label(self._home_frame, text="", bg=BG_SECONDARY,
                                    fg=TEXT_PRIMARY, font=FONT_SCORE, anchor="e")
        self._home_score.pack(side="right")

        # Status row
        self._status_frame = tk.Frame(self._content, bg=BG_SECONDARY)
        self._status_frame.pack(fill="x", pady=(4, 0))
        self._status_lbl = tk.Label(self._status_frame, text="", bg=BG_SECONDARY,
                                    fg=TEXT_SECONDARY, font=FONT_SMALL, anchor="w")
        self._status_lbl.pack(side="left")
        self._upset_lbl = tk.Label(self._status_frame, text="", bg=BG_SECONDARY,
                                   fg=UPSET_GOLD, font=FONT_SMALL, anchor="e")
        self._upset_lbl.pack(side="right")

        self.update_game(game)

    def update_game(self, game: Game):
        """Refresh displayed data."""
        away = game.away
        home = game.home

        if away:
            self._away_seed.configure(text=f"({away.seed})" if away.seed else "")
            self._away_color.configure(bg=away.color)
            self._away_name.configure(text=away.abbrev)
            self._away_score.configure(
                text=away.score if game.state != "pre" else "")
        if home:
            self._home_seed.configure(text=f"({home.seed})" if home.seed else "")
            self._home_color.configure(bg=home.color)
            self._home_name.configure(text=home.abbrev)
            self._home_score.configure(
                text=home.score if game.state != "pre" else "")

        # Status
        status_parts = []
        if game.is_live:
            status_parts.append("\u25cf LIVE")
            self._status_lbl.configure(fg=LIVE_GREEN)
        else:
            self._status_lbl.configure(fg=TEXT_SECONDARY)
        status_parts.append(game.short_detail or game.detail or "")
        self._status_lbl.configure(text="  ".join(status_parts))

        self._upset_lbl.configure(
            text="\u26a1 UPSET" if game.is_upset else "")

    # ── Drag support ───────────────────────────────────────────────────────
    def _on_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.winfo_x() + event.x - self._drag_data["x"]
        y = self.winfo_y() + event.y - self._drag_data["y"]
        self.geometry(f"+{x}+{y}")
