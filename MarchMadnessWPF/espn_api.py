"""ESPN API client for March Madness scoreboard data."""

import requests
import logging
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional

log = logging.getLogger(__name__)

BASE_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/basketball/"
    "mens-college-basketball/scoreboard"
)
GROUP_MARCH_MADNESS = "100"
TIMEOUT = 8  # seconds


# ── Parsed data classes ────────────────────────────────────────────────────
class Team:
    __slots__ = ("id", "abbrev", "name", "color", "logo_url", "score", "seed",
                 "home_away")

    def __init__(self, data: dict):
        team = data.get("team", {})
        self.id = team.get("id", "")
        self.abbrev = team.get("abbreviation", "???")
        self.name = team.get("displayName", "Unknown")
        self.color = "#" + team.get("color", "333333")
        self.logo_url = team.get("logo", "")
        self.score = data.get("score", "0")
        rank = data.get("curatedRank", {})
        self.seed = rank.get("current", 0) if rank.get("current", 99) <= 16 else 0
        self.home_away = data.get("homeAway", "")


class Game:
    __slots__ = ("id", "name", "short_name", "date", "state", "detail",
                 "short_detail", "period", "clock", "home", "away",
                 "venue", "broadcast", "round_label", "is_upset",
                 "is_close")

    def __init__(self, event: dict):
        self.id = event.get("id", "")
        self.name = event.get("name", "")
        self.short_name = event.get("shortName", "")
        self.date = event.get("date", "")

        status = event.get("status", {})
        stype = status.get("type", {})
        self.state = stype.get("state", "pre")
        self.detail = stype.get("detail", "")
        self.short_detail = stype.get("shortDetail", "")
        self.period = status.get("period", 0)
        self.clock = status.get("displayClock", "")

        comp = event.get("competitions", [{}])[0]
        competitors = comp.get("competitors", [])
        self.home = None
        self.away = None
        for c in competitors:
            t = Team(c)
            if t.home_away == "home":
                self.home = t
            else:
                self.away = t
        # Fallback if homeAway missing
        if self.home is None and len(competitors) >= 2:
            self.home = Team(competitors[0])
            self.away = Team(competitors[1])
        elif self.home is None and competitors:
            self.home = Team(competitors[0])
            self.away = Team({"team": {"abbreviation": "TBD"}})

        venue_data = comp.get("venue", {})
        self.venue = venue_data.get("fullName", "")

        broadcasts = comp.get("broadcasts", [])
        if broadcasts:
            names = broadcasts[0].get("names", [])
            self.broadcast = names[0] if names else ""
        else:
            self.broadcast = ""

        notes = event.get("notes", [])
        self.round_label = notes[0].get("headline", "") if notes else ""

        # Upset detection
        self.is_upset = False
        if self.home and self.away and self.state in ("in", "post"):
            self._detect_upset()

        # Close game detection
        self.is_close = False
        if self.state == "in":
            self._detect_close()

    def _detect_upset(self):
        try:
            h_score = int(self.home.score)
            a_score = int(self.away.score)
        except (ValueError, TypeError):
            return
        h_seed = self.home.seed or 99
        a_seed = self.away.seed or 99
        if h_seed < a_seed and a_score > h_score:
            self.is_upset = True
        elif a_seed < h_seed and h_score > a_score:
            self.is_upset = True

    def _detect_close(self):
        try:
            diff = abs(int(self.home.score) - int(self.away.score))
        except (ValueError, TypeError):
            return
        half = self.period or 1
        if half >= 2 and diff <= 5:
            self.is_close = True

    @property
    def is_live(self) -> bool:
        return self.state == "in"


# ── API functions ──────────────────────────────────────────────────────────
def fetch_scoreboard(date: Optional[str] = None) -> list[Game]:
    """Fetch today's March Madness scoreboard. `date` is YYYYMMDD or None."""
    params = {"groups": GROUP_MARCH_MADNESS}
    if date:
        params["dates"] = date
    try:
        resp = requests.get(BASE_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log.warning("ESPN API error: %s", e)
        return []
    events = data.get("events", [])
    return [Game(ev) for ev in events]


def fetch_tournament_games(start_date: str = "20260317",
                           end_date: str = "20260408") -> list[Game]:
    """Fetch games across the tournament date range."""
    all_games: list[Game] = []
    current = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    while current <= end:
        ds = current.strftime("%Y%m%d")
        games = fetch_scoreboard(ds)
        all_games.extend(games)
        current += timedelta(days=1)
    return all_games


def fetch_logo_bytes(url: str) -> Optional[bytes]:
    """Download a team logo image. Returns raw bytes or None."""
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        log.debug("Logo fetch failed: %s", e)
        return None
