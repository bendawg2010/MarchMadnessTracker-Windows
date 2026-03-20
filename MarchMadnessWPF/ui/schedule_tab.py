"""Schedule tab - shows upcoming and recent games by date."""

import tkinter as tk
import tkinter.ttk as ttk
import threading
from datetime import datetime, timedelta
from ui.styles import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_DIM, LIVE_GREEN, ACCENT, BORDER,
    FONT_BODY, FONT_BODY_BOLD, FONT_HEADING, FONT_SMALL,
    CARD_PAD_X, CARD_PAD_Y,
)
from espn_api import fetch_scoreboard, Game


class ScheduleTab(ttk.Frame):
    """Shows game schedule across multiple days."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._widgets: list[tk.Widget] = []

        # Date navigation
        nav = ttk.Frame(self)
        nav.pack(fill="x", padx=CARD_PAD_X, pady=6)

        self._date = datetime.now()
        self._date_label = ttk.Label(nav, text="", font=FONT_HEADING)
        self._date_label.pack(side="left", expand=True)

        prev_btn = ttk.Button(nav, text="\u25c0 Prev", width=8,
                              command=self._prev_day)
        prev_btn.pack(side="left", padx=4)
        today_btn = ttk.Button(nav, text="Today", width=8,
                               command=self._go_today)
        today_btn.pack(side="left", padx=4)
        next_btn = ttk.Button(nav, text="Next \u25b6", width=8,
                              command=self._next_day)
        next_btn.pack(side="left", padx=4)

        # Scrollable area
        self._canvas = tk.Canvas(self, bg=BG_PRIMARY, highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical",
                                        command=self._canvas.yview)
        self._inner = ttk.Frame(self._canvas)
        self._inner_id = self._canvas.create_window((0, 0), window=self._inner,
                                                     anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner.bind("<Configure>",
                         lambda e: self._canvas.configure(
                             scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(
                              self._inner_id, width=e.width))

        self._loading = ttk.Label(self._inner, text="Loading schedule...",
                                  font=FONT_BODY, foreground=TEXT_SECONDARY)
        self._update_date_display()
        self._load_day()

    def _update_date_display(self):
        self._date_label.configure(
            text=self._date.strftime("%A, %B %d, %Y"))

    def _prev_day(self):
        self._date -= timedelta(days=1)
        self._update_date_display()
        self._load_day()

    def _next_day(self):
        self._date += timedelta(days=1)
        self._update_date_display()
        self._load_day()

    def _go_today(self):
        self._date = datetime.now()
        self._update_date_display()
        self._load_day()

    def _load_day(self):
        for w in self._widgets:
            w.destroy()
        self._widgets.clear()
        self._loading.pack(pady=40)

        ds = self._date.strftime("%Y%m%d")
        threading.Thread(target=self._fetch, args=(ds,), daemon=True).start()

    def _fetch(self, date_str: str):
        games = fetch_scoreboard(date_str)
        try:
            self.after(0, lambda: self._render(games))
        except Exception:
            pass

    def _render(self, games: list[Game]):
        self._loading.pack_forget()
        for w in self._widgets:
            w.destroy()
        self._widgets.clear()

        if not games:
            lbl = ttk.Label(self._inner,
                            text="No tournament games scheduled for this date.",
                            font=FONT_BODY, foreground=TEXT_SECONDARY,
                            justify="center")
            lbl.pack(pady=40)
            self._widgets.append(lbl)
            return

        for game in games:
            card = self._build_schedule_card(game)
            card.pack(fill="x", padx=CARD_PAD_X, pady=CARD_PAD_Y)
            self._widgets.append(card)

    def _build_schedule_card(self, game: Game) -> tk.Frame:
        card = tk.Frame(self._inner, bg=BG_SECONDARY, padx=10, pady=8)

        # Top: round info
        if game.round_label:
            tk.Label(card, text=game.round_label, bg=BG_SECONDARY,
                     fg=TEXT_DIM, font=FONT_SMALL, anchor="w").pack(
                         anchor="w")

        # Matchup
        away_str = self._team_str(game.away)
        home_str = self._team_str(game.home)

        matchup_frame = tk.Frame(card, bg=BG_SECONDARY)
        matchup_frame.pack(fill="x", pady=2)

        tk.Label(matchup_frame, text=f"{away_str}  vs  {home_str}",
                 bg=BG_SECONDARY, fg=TEXT_PRIMARY, font=FONT_BODY_BOLD,
                 anchor="w").pack(side="left")

        # Time / status
        if game.state == "pre":
            status_text = game.detail or "Scheduled"
            status_fg = TEXT_SECONDARY
        elif game.state == "in":
            score = f"{game.away.score}-{game.home.score}" if game.away and game.home else ""
            status_text = f"\u25cf LIVE  {score}  {game.short_detail}"
            status_fg = LIVE_GREEN
        else:
            score = f"{game.away.score}-{game.home.score}" if game.away and game.home else ""
            status_text = f"Final  {score}"
            status_fg = TEXT_DIM

        tk.Label(matchup_frame, text=status_text, bg=BG_SECONDARY,
                 fg=status_fg, font=FONT_SMALL, anchor="e").pack(side="right")

        # Venue / broadcast
        info_parts = []
        if game.venue:
            info_parts.append(game.venue)
        if game.broadcast:
            info_parts.append(game.broadcast)
        if info_parts:
            tk.Label(card, text="  |  ".join(info_parts), bg=BG_SECONDARY,
                     fg=TEXT_DIM, font=FONT_SMALL, anchor="w").pack(anchor="w")

        # Bottom border
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=(6, 0))

        return card

    @staticmethod
    def _team_str(team) -> str:
        if team is None:
            return "TBD"
        seed = f"({team.seed}) " if team.seed else ""
        return f"{seed}{team.abbrev}"
