"""Bracket tab - displays tournament bracket organized by round."""

import tkinter as tk
import tkinter.ttk as ttk
import threading
from ui.styles import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_DIM, LIVE_GREEN, UPSET_GOLD, ACCENT, BORDER,
    FONT_BODY, FONT_BODY_BOLD, FONT_HEADING, FONT_SMALL, FONT_SEED,
    CARD_PAD_X, CARD_PAD_Y,
)
from espn_api import fetch_tournament_games, Game

# Round ordering based on typical NCAA tournament round names
ROUND_ORDER = [
    "First Four",
    "1st Round", "First Round",
    "2nd Round", "Second Round",
    "Sweet 16", "Sweet Sixteen",
    "Elite 8", "Elite Eight",
    "Final Four",
    "National Championship", "Championship",
]


def _round_sort_key(label: str) -> int:
    low = label.lower().strip()
    for i, r in enumerate(ROUND_ORDER):
        if r.lower() in low:
            return i
    return 99


class BracketTab(ttk.Frame):
    """Shows the tournament bracket grouped by round."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._games_by_round: dict[str, list[Game]] = {}
        self._widgets: list[tk.Widget] = []

        # Scrollable canvas
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
        self._canvas.bind_all("<MouseWheel>",
                              lambda e: self._canvas.yview_scroll(
                                  int(-1 * (e.delta / 120)), "units"))

        # Loading label
        self._loading = ttk.Label(self._inner,
                                  text="Loading bracket data...",
                                  font=FONT_BODY, foreground=TEXT_SECONDARY)
        self._loading.pack(pady=40)

        # Fetch in background
        self._fetch_thread = threading.Thread(target=self._fetch, daemon=True)
        self._fetch_thread.start()

    def _fetch(self):
        games = fetch_tournament_games()
        # Group by round
        by_round: dict[str, list[Game]] = {}
        for g in games:
            label = g.round_label or "Other"
            # Extract just the round portion
            parts = label.split(" - ")
            round_name = parts[-1].strip() if parts else label
            by_round.setdefault(round_name, []).append(g)
        self._games_by_round = by_round
        # Update UI on main thread
        try:
            self.after(0, self._render)
        except Exception:
            pass

    def _render(self):
        for w in self._widgets:
            w.destroy()
        self._widgets.clear()
        self._loading.pack_forget()

        if not self._games_by_round:
            lbl = ttk.Label(self._inner,
                            text="No bracket data available yet.\n"
                                 "Games will appear once the tournament starts.",
                            font=FONT_BODY, foreground=TEXT_SECONDARY,
                            justify="center")
            lbl.pack(pady=40)
            self._widgets.append(lbl)
            return

        # Sort rounds
        sorted_rounds = sorted(self._games_by_round.keys(),
                               key=_round_sort_key)

        for round_name in sorted_rounds:
            games = self._games_by_round[round_name]
            section = self._build_round_section(round_name, games)
            section.pack(fill="x", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
            self._widgets.append(section)

    def _build_round_section(self, round_name: str,
                             games: list[Game]) -> ttk.Frame:
        frame = ttk.Frame(self._inner)

        # Round header
        header = tk.Frame(frame, bg=ACCENT, height=28)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"  {round_name}  ({len(games)} games)",
                 bg=ACCENT, fg="white", font=FONT_BODY_BOLD,
                 anchor="w").pack(fill="x", padx=8, pady=2)

        # Game matchups
        for g in games:
            matchup = self._build_matchup(frame, g)
            matchup.pack(fill="x", pady=1)

        return frame

    def _build_matchup(self, parent, game: Game) -> tk.Frame:
        f = tk.Frame(parent, bg=BG_SECONDARY, padx=8, pady=4)

        away = game.away
        home = game.home

        # Away line
        away_text = self._team_str(away)
        away_score = away.score if away and game.state != "pre" else ""
        tk.Label(f, text=away_text, bg=BG_SECONDARY, fg=TEXT_PRIMARY,
                 font=FONT_BODY, anchor="w").pack(side="top", anchor="w")

        # Home line
        home_text = self._team_str(home)
        home_score = home.score if home and game.state != "pre" else ""

        row = tk.Frame(f, bg=BG_SECONDARY)
        row.pack(fill="x")
        tk.Label(row, text=home_text, bg=BG_SECONDARY, fg=TEXT_PRIMARY,
                 font=FONT_BODY, anchor="w").pack(side="left")

        # Status on right
        state_fg = LIVE_GREEN if game.is_live else TEXT_DIM
        detail = game.short_detail or game.detail or ""
        if game.state == "post" and away_score and home_score:
            detail = f"{away_score}-{home_score}  {detail}"
        elif game.state == "in" and away_score and home_score:
            detail = f"{away_score}-{home_score}  {detail}"

        status_text = detail
        if game.is_upset:
            status_text += "  \u26a1"

        tk.Label(row, text=status_text, bg=BG_SECONDARY, fg=state_fg,
                 font=FONT_SMALL, anchor="e").pack(side="right")

        # Separator
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=(4, 0))

        return f

    @staticmethod
    def _team_str(team) -> str:
        if team is None:
            return "TBD"
        seed = f"({team.seed}) " if team.seed else ""
        return f"{seed}{team.abbrev}"

    def refresh(self):
        """Re-fetch bracket data."""
        self._loading.pack(pady=40)
        threading.Thread(target=self._fetch, daemon=True).start()
