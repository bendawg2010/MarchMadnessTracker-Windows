"""Background polling thread for live score updates."""

import threading
import time
import logging
from typing import Callable, Optional
from espn_api import fetch_scoreboard, Game

log = logging.getLogger(__name__)

POLL_LIVE = 3       # seconds when a game is live
POLL_IDLE = 20      # seconds when no live games


class ScorePoller:
    """Polls ESPN scoreboard on a background thread and calls back with data."""

    def __init__(self, on_update: Callable[[list[Game]], None],
                 on_close_game: Optional[Callable[[Game], None]] = None):
        self._on_update = on_update
        self._on_close_game = on_close_game
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._games: list[Game] = []
        self._alerted_close: set[str] = set()  # game IDs already alerted

    # ── Public API ─────────────────────────────────────────────────────────
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name="ScorePoller")
        self._thread.start()
        log.info("ScorePoller started")

    def stop(self):
        self._stop_event.set()
        log.info("ScorePoller stopped")

    @property
    def games(self) -> list[Game]:
        with self._lock:
            return list(self._games)

    # ── Internal ───────────────────────────────────────────────────────────
    def _run(self):
        while not self._stop_event.is_set():
            try:
                games = fetch_scoreboard()
            except Exception as e:
                log.error("Poll error: %s", e)
                games = []

            with self._lock:
                self._games = games

            # Determine interval
            any_live = any(g.is_live for g in games)
            interval = POLL_LIVE if any_live else POLL_IDLE

            # Callback
            try:
                self._on_update(games)
            except Exception as e:
                log.error("Update callback error: %s", e)

            # Close-game alerts
            if self._on_close_game:
                for g in games:
                    if g.is_close and g.id not in self._alerted_close:
                        self._alerted_close.add(g.id)
                        try:
                            self._on_close_game(g)
                        except Exception as e:
                            log.error("Close game callback error: %s", e)

            self._stop_event.wait(interval)
