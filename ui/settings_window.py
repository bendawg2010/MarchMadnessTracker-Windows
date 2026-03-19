"""Settings panel window."""

import tkinter as tk
import tkinter.ttk as ttk
import json
import os
from ui.styles import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, FONT_BODY, FONT_BODY_BOLD, FONT_HEADING, FONT_TITLE,
    CARD_PAD_X,
    apply_dark_theme,
)

SETTINGS_FILE = os.path.join(os.path.expanduser("~"),
                             ".marchmadness_settings.json")

DEFAULT_SETTINGS = {
    "favorite_team": "",
    "notifications_enabled": True,
    "ticker_enabled": False,
    "ticker_height": 32,
    "auto_start_polling": True,
}


def load_settings() -> dict:
    """Load settings from disk, returning defaults for missing keys."""
    settings = dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r") as f:
            saved = json.load(f)
            settings.update(saved)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return settings


def save_settings(settings: dict):
    """Persist settings to disk."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


class SettingsWindow(tk.Toplevel):
    """Settings dialog."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.title("Settings")
        self.configure(bg=BG_PRIMARY)
        self.geometry("400x420")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        apply_dark_theme(self)

        self._settings = load_settings()

        # Title
        ttk.Label(self, text="Settings", font=FONT_TITLE).pack(
            pady=(16, 12), padx=CARD_PAD_X, anchor="w")

        # ── Favorite Team ──────────────────────────────────────────────────
        fav_frame = ttk.Frame(self)
        fav_frame.pack(fill="x", padx=CARD_PAD_X, pady=6)
        ttk.Label(fav_frame, text="Favorite Team (abbreviation):",
                  font=FONT_BODY_BOLD).pack(anchor="w")
        self._fav_var = tk.StringVar(value=self._settings.get("favorite_team", ""))
        fav_entry = ttk.Entry(fav_frame, textvariable=self._fav_var, width=20)
        fav_entry.pack(anchor="w", pady=4)
        ttk.Label(fav_frame, text="e.g. DUKE, UNC, GONZ, KU",
                  font=("Segoe UI", 9), foreground=TEXT_SECONDARY).pack(anchor="w")

        # ── Notifications ──────────────────────────────────────────────────
        self._notif_var = tk.BooleanVar(
            value=self._settings.get("notifications_enabled", True))
        ttk.Checkbutton(self, text="Enable close-game notifications",
                        variable=self._notif_var).pack(
            fill="x", padx=CARD_PAD_X, pady=8, anchor="w")

        # ── Ticker ─────────────────────────────────────────────────────────
        self._ticker_var = tk.BooleanVar(
            value=self._settings.get("ticker_enabled", False))
        ttk.Checkbutton(self, text="Show floating ticker bar",
                        variable=self._ticker_var).pack(
            fill="x", padx=CARD_PAD_X, pady=4, anchor="w")

        ticker_size_frame = ttk.Frame(self)
        ticker_size_frame.pack(fill="x", padx=CARD_PAD_X, pady=4)
        ttk.Label(ticker_size_frame, text="Ticker height:",
                  font=FONT_BODY).pack(side="left")
        self._ticker_height_var = tk.IntVar(
            value=self._settings.get("ticker_height", 32))
        tk.Scale(ticker_size_frame, from_=24, to=56, orient="horizontal",
                 variable=self._ticker_height_var, bg=BG_PRIMARY,
                 fg=TEXT_PRIMARY, troughcolor=BG_SECONDARY,
                 highlightthickness=0, length=160).pack(side="left", padx=8)

        # ── Auto polling ───────────────────────────────────────────────────
        self._auto_poll_var = tk.BooleanVar(
            value=self._settings.get("auto_start_polling", True))
        ttk.Checkbutton(self, text="Auto-start score polling on launch",
                        variable=self._auto_poll_var).pack(
            fill="x", padx=CARD_PAD_X, pady=8, anchor="w")

        # ── Buttons ────────────────────────────────────────────────────────
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=CARD_PAD_X, pady=(20, 12))

        ttk.Button(btn_frame, text="Save", style="Accent.TButton",
                   command=self._save).pack(side="right", padx=4)
        ttk.Button(btn_frame, text="Cancel",
                   command=self.destroy).pack(side="right", padx=4)

    def _save(self):
        self._settings["favorite_team"] = self._fav_var.get().strip().upper()
        self._settings["notifications_enabled"] = self._notif_var.get()
        self._settings["ticker_enabled"] = self._ticker_var.get()
        self._settings["ticker_height"] = self._ticker_height_var.get()
        self._settings["auto_start_polling"] = self._auto_poll_var.get()

        save_settings(self._settings)

        # Apply settings live
        self.app.apply_settings(self._settings)
        self.destroy()
