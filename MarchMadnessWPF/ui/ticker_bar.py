"""Floating ticker bar at top of screen showing scrolling live scores."""

import tkinter as tk
from ui.styles import (
    BG_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, TEXT_SECONDARY, LIVE_GREEN,
    UPSET_GOLD, ACCENT, FONT_TICKER, FONT_SMALL, TICKER_HEIGHT,
)
from espn_api import Game


class TickerBar(tk.Toplevel):
    """Borderless always-on-top ticker bar at the top of the screen."""

    def __init__(self, master, width: int = 0):
        super().__init__(master)
        self.title("March Madness Ticker")
        self.configure(bg=BG_SECONDARY)
        self.overrideredirect(True)       # No title bar
        self.attributes("-topmost", True)

        # Get screen width
        screen_w = width or self.winfo_screenwidth()
        self._ticker_width = screen_w
        self.geometry(f"{screen_w}x{TICKER_HEIGHT}+0+0")

        # Allow dragging
        self._drag_data = {"x": 0, "y": 0}
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)

        # Right-click to close
        self.bind("<Button-3>", lambda e: self.hide())

        # Canvas for scrolling text
        self._canvas = tk.Canvas(self, bg=BG_SECONDARY, highlightthickness=0,
                                 height=TICKER_HEIGHT)
        self._canvas.pack(fill="both", expand=True)

        # Ticker state
        self._text_items: list[int] = []
        self._ticker_text = ""
        self._scroll_x = 0
        self._text_id = None
        self._running = False
        self._visible = False

        # Close button on the right
        self._close_btn = tk.Button(
            self, text="\u2715", bg=BG_SECONDARY, fg=TEXT_SECONDARY,
            font=FONT_SMALL, bd=0, cursor="hand2",
            activebackground=ACCENT, activeforeground="white",
            command=self.hide,
        )
        self._close_btn.place(relx=1.0, x=-2, rely=0.5, anchor="e")

        # Start hidden
        self.withdraw()

    def show(self):
        self._visible = True
        self.deiconify()
        self.lift()
        if not self._running:
            self._running = True
            self._scroll()

    def hide(self):
        self._visible = False
        self._running = False
        self.withdraw()

    @property
    def visible(self) -> bool:
        return self._visible

    def toggle(self):
        if self._visible:
            self.hide()
        else:
            self.show()

    def set_size(self, height: int):
        """Adjust ticker height."""
        self.geometry(f"{self._ticker_width}x{height}+0+0")
        self._canvas.configure(height=height)

    def update_scores(self, games: list[Game]):
        """Build ticker text from current games."""
        parts = []
        for g in games:
            if g.away is None or g.home is None:
                continue
            if g.state == "pre":
                part = f"{g.away.abbrev} vs {g.home.abbrev} - {g.short_detail or g.detail}"
            elif g.state == "in":
                part = (f"\u25cf {g.away.abbrev} {g.away.score} - "
                        f"{g.home.abbrev} {g.home.score}  {g.short_detail}")
                if g.is_upset:
                    part += " \u26a1UPSET"
            else:
                part = (f"{g.away.abbrev} {g.away.score} - "
                        f"{g.home.abbrev} {g.home.score}  FINAL")
                if g.is_upset:
                    part += " \u26a1UPSET"
            parts.append(part)

        self._ticker_text = "     \u2022     ".join(parts) if parts else "March Madness Tracker - No games right now"
        self._rebuild_text()

    def _rebuild_text(self):
        if self._text_id is not None:
            self._canvas.delete(self._text_id)
        self._scroll_x = self._ticker_width
        self._text_id = self._canvas.create_text(
            self._scroll_x, TICKER_HEIGHT // 2,
            text=self._ticker_text, fill=TEXT_PRIMARY, font=FONT_TICKER,
            anchor="w",
        )

    def _scroll(self):
        if not self._running or not self._visible:
            return
        if self._text_id is None:
            self._rebuild_text()

        self._scroll_x -= 2  # pixels per frame
        self._canvas.coords(self._text_id, self._scroll_x, TICKER_HEIGHT // 2)

        # Reset when fully scrolled off left
        bbox = self._canvas.bbox(self._text_id)
        if bbox and bbox[2] < 0:
            self._scroll_x = self._ticker_width

        self.after(30, self._scroll)  # ~33 fps

    # ── Drag ───────────────────────────────────────────────────────────────
    def _on_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.winfo_x() + event.x - self._drag_data["x"]
        y = self.winfo_y() + event.y - self._drag_data["y"]
        self.geometry(f"{self._ticker_width}x{TICKER_HEIGHT}+{x}+{y}")
