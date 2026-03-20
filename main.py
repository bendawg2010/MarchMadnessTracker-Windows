"""
March Madness Tracker - Windows System Tray Application
========================================================
Entry point. Manages the tkinter root, system tray, polling, and all windows.
"""

import sys
import os
import tkinter as tk
import logging
import threading

# Ensure the app directory is on the path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from score_poller import ScorePoller
from tray_icon import TrayIcon
from notifications import notify_close_game
from ui.main_window import MainWindow
from ui.ticker_bar import TickerBar
from ui.score_widget import ScoreWidget
from ui.settings_window import SettingsWindow, load_settings, save_settings
from espn_api import Game

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("main")


class MarchMadnessApp:
    """Top-level application controller."""

    def __init__(self):
        self._settings = load_settings()

        # Root tkinter window (hidden)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("March Madness Tracker")

        # Windows
        self._main_window: MainWindow | None = None
        self._ticker: TickerBar | None = None
        self._score_widgets: dict[str, ScoreWidget] = {}
        self._settings_window: SettingsWindow | None = None

        # Create ticker (hidden by default)
        self._ticker = TickerBar(self.root)

        # Poller
        self._poller = ScorePoller(
            on_update=self._on_scores_update,
            on_close_game=self._on_close_game,
        )

        # System tray
        self._tray = TrayIcon(
            on_open=self._schedule(self.show_main_window),
            on_ticker=self._schedule(self.toggle_ticker),
            on_settings=self._schedule(self.open_settings),
            on_quit=self._schedule(self.quit_app),
        )

        # Latest games cache
        self._games: list[Game] = []

    def _schedule(self, fn):
        """Return a wrapper that schedules `fn` on the tkinter main thread."""
        def wrapper(*args, **kwargs):
            self.root.after(0, lambda: fn(*args, **kwargs))
        return wrapper

    # ── Lifecycle ──────────────────────────────────────────────────────────
    def run(self):
        """Start the application."""
        log.info("Starting March Madness Tracker")
        self._tray.start()
        self._poller.start()

        # Apply saved settings
        if self._settings.get("ticker_enabled"):
            self._ticker.show()

        # Show main window on startup
        self.show_main_window()

        # Start tkinter main loop
        self.root.mainloop()

    def quit_app(self):
        """Clean shutdown."""
        log.info("Shutting down")
        self._poller.stop()
        self._tray.stop()

        # Close all score widgets
        for w in list(self._score_widgets.values()):
            try:
                w.destroy()
            except Exception:
                pass

        if self._ticker:
            try:
                self._ticker.destroy()
            except Exception:
                pass

        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

        # Force exit (tray thread may linger)
        os._exit(0)

    # ── Window management ──────────────────────────────────────────────────
    def show_main_window(self):
        if self._main_window is None or not self._main_window.winfo_exists():
            self._main_window = MainWindow(self.root, self)
            # Push current data
            if self._games:
                self._main_window.scores_tab.update_games(self._games)
                self._main_window.update_status(self._games)
        else:
            self._main_window.show()

    def toggle_ticker(self):
        if self._ticker:
            self._ticker.toggle()

    def open_settings(self):
        if (self._settings_window is not None
                and self._settings_window.winfo_exists()):
            self._settings_window.lift()
            return
        self._settings_window = SettingsWindow(self.root, self)

    def open_score_widget(self, game: Game):
        """Open or update a floating score widget for a game."""
        if game.id in self._score_widgets:
            w = self._score_widgets[game.id]
            if w.winfo_exists():
                w.update_game(game)
                w.lift()
                return
        widget = ScoreWidget(self.root, game)
        self._score_widgets[game.id] = widget
        widget.bind("<Destroy>",
                    lambda e, gid=game.id: self._score_widgets.pop(gid, None))

    def apply_settings(self, settings: dict):
        """Apply changed settings live."""
        self._settings = settings

        # Ticker visibility
        if self._ticker:
            if settings.get("ticker_enabled"):
                self._ticker.set_size(settings.get("ticker_height", 32))
                self._ticker.show()
            else:
                self._ticker.hide()

    # ── Score update callbacks ─────────────────────────────────────────────
    def _on_scores_update(self, games: list[Game]):
        """Called from poller thread with fresh data."""
        self._games = games

        # Schedule UI updates on main thread
        self.root.after(0, lambda: self._update_ui(games))

    def _update_ui(self, games: list[Game]):
        """Update all UI components (runs on main thread)."""
        # Main window scores tab
        if self._main_window and self._main_window.winfo_exists():
            self._main_window.scores_tab.update_games(games)
            self._main_window.update_status(games)

        # Ticker
        if self._ticker and self._ticker.visible:
            self._ticker.update_scores(games)

        # Score widgets
        for game in games:
            if game.id in self._score_widgets:
                w = self._score_widgets[game.id]
                if w.winfo_exists():
                    w.update_game(game)

        # Tray tooltip
        live = [g for g in games if g.is_live]
        if live:
            tip_parts = []
            for g in live[:3]:
                if g.away and g.home:
                    tip_parts.append(
                        f"{g.away.abbrev} {g.away.score}-{g.home.score} {g.home.abbrev}")
            tip = "LIVE: " + " | ".join(tip_parts)
        else:
            tip = f"March Madness - {len(games)} games today"
        self._tray.update_tooltip(tip)

    def _on_close_game(self, game: Game):
        """Called from poller thread for close-game alerts."""
        if self._settings.get("notifications_enabled", True):
            notify_close_game(game)


# ── Entry Point ────────────────────────────────────────────────────────────
def main():
    app = MarchMadnessApp()
    app.run()


if __name__ == "__main__":
    main()
