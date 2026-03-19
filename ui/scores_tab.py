"""Scores tab - displays live/recent game cards."""

import tkinter as tk
import tkinter.ttk as ttk
from io import BytesIO
from typing import Optional
from ui.styles import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_DIM, LIVE_GREEN, UPSET_GOLD, ACCENT, FINAL_GRAY, BORDER,
    FONT_BODY, FONT_BODY_BOLD, FONT_HEADING, FONT_SCORE, FONT_SMALL,
    FONT_SEED, CARD_PAD_X, CARD_PAD_Y, STATUS_COLORS,
)

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from espn_api import Game, fetch_logo_bytes


class ScoresTab(ttk.Frame):
    """Scrollable list of game score cards."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._logo_cache: dict[str, Optional[ImageTk.PhotoImage]] = {}
        self._widgets: list[tk.Widget] = []

        # Scrollable canvas
        self._canvas = tk.Canvas(self, bg=BG_PRIMARY, highlightthickness=0,
                                 borderwidth=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical",
                                        command=self._canvas.yview)
        self._inner = ttk.Frame(self._canvas)
        self._inner_id = self._canvas.create_window((0, 0), window=self._inner,
                                                     anchor="nw")

        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # No-games label
        self._empty_label = ttk.Label(
            self._inner, text="No tournament games right now.\nWaiting for data...",
            font=FONT_BODY, foreground=TEXT_SECONDARY, anchor="center",
            justify="center",
        )

    def _on_inner_configure(self, _event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._inner_id, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Public ─────────────────────────────────────────────────────────────
    def update_games(self, games: list[Game]):
        """Rebuild game cards. Called from main thread."""
        for w in self._widgets:
            w.destroy()
        self._widgets.clear()

        if not games:
            self._empty_label.pack(pady=40)
            self._widgets.append(self._empty_label)
            return

        self._empty_label.pack_forget()
        for game in games:
            card = self._build_card(game)
            card.pack(fill="x", padx=CARD_PAD_X, pady=CARD_PAD_Y)
            self._widgets.append(card)

    # ── Card builder ───────────────────────────────────────────────────────
    def _build_card(self, game: Game) -> ttk.Frame:
        card = ttk.Frame(self._inner, style="Card.TFrame")
        card.columnconfigure(1, weight=1)

        # Row 0: round label / broadcast
        header_text = game.round_label or ""
        if game.broadcast:
            header_text += f"  |  {game.broadcast}" if header_text else game.broadcast
        if header_text:
            lbl = ttk.Label(card, text=header_text, style="CardDim.TLabel",
                            font=FONT_SMALL)
            lbl.grid(row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(6, 2))

        # Row 1: away team
        self._team_row(card, game.away, row=1, game=game)
        # Row 2: home team
        self._team_row(card, game.home, row=2, game=game)

        # Row 3: status line
        state_color = STATUS_COLORS.get(game.state, TEXT_SECONDARY)
        status_text = game.short_detail or game.detail
        status_parts = []
        if game.is_live:
            status_parts.append("\u25cf LIVE")
        status_parts.append(status_text)

        status_lbl = tk.Label(card, text="  ".join(status_parts),
                              bg=BG_SECONDARY, fg=state_color, font=FONT_SMALL,
                              anchor="w")
        status_lbl.grid(row=3, column=0, columnspan=3, sticky="w", padx=8,
                        pady=(0, 2))

        # Upset badge
        if game.is_upset:
            upset_lbl = tk.Label(card, text="\u26a1 UPSET", bg=BG_SECONDARY,
                                 fg=UPSET_GOLD, font=FONT_SMALL)
            upset_lbl.grid(row=3, column=3, sticky="e", padx=8)

        # Pop-out button
        pop_btn = tk.Button(
            card, text="\u2197", bg=BG_SECONDARY, fg=TEXT_DIM,
            font=FONT_SMALL, bd=0, cursor="hand2",
            activebackground=BG_TERTIARY, activeforeground=TEXT_PRIMARY,
            command=lambda g=game: self.app.open_score_widget(g),
        )
        pop_btn.grid(row=1, column=3, rowspan=2, padx=(0, 6))

        # Bottom border
        sep = tk.Frame(card, bg=BORDER, height=1)
        sep.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(4, 0))

        return card

    def _team_row(self, card, team, row, game):
        if team is None:
            ttk.Label(card, text="TBD", style="Card.TLabel").grid(
                row=row, column=0, columnspan=3, sticky="w", padx=8, pady=2)
            return

        # Seed
        seed_text = f"({team.seed})" if team.seed else ""
        seed_lbl = tk.Label(card, text=seed_text, bg=BG_SECONDARY,
                            fg=TEXT_DIM, font=FONT_SEED, width=4, anchor="e")
        seed_lbl.grid(row=row, column=0, sticky="e", padx=(8, 2), pady=2)

        # Team name with color bar
        name_frame = tk.Frame(card, bg=BG_SECONDARY)
        name_frame.grid(row=row, column=1, sticky="w", pady=2)
        color_bar = tk.Frame(name_frame, bg=team.color, width=3, height=18)
        color_bar.pack(side="left", padx=(0, 6))
        name_lbl = tk.Label(name_frame, text=team.abbrev, bg=BG_SECONDARY,
                            fg=TEXT_PRIMARY, font=FONT_BODY_BOLD, anchor="w")
        name_lbl.pack(side="left")

        # Score
        try:
            score_val = team.score if game.state != "pre" else ""
        except Exception:
            score_val = ""
        score_lbl = tk.Label(card, text=score_val, bg=BG_SECONDARY,
                             fg=TEXT_PRIMARY, font=FONT_BODY_BOLD, width=4,
                             anchor="e")
        score_lbl.grid(row=row, column=2, sticky="e", padx=4, pady=2)

    # ── Logo helpers ───────────────────────────────────────────────────────
    def _get_logo(self, url: str, size: int = 24) -> Optional["ImageTk.PhotoImage"]:
        if not HAS_PIL or not url:
            return None
        if url in self._logo_cache:
            return self._logo_cache[url]
        raw = fetch_logo_bytes(url)
        if raw is None:
            self._logo_cache[url] = None
            return None
        try:
            img = Image.open(BytesIO(raw)).resize((size, size), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._logo_cache[url] = photo
            return photo
        except Exception:
            self._logo_cache[url] = None
            return None
