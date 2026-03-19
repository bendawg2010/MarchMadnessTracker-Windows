"""System tray icon management using pystray."""

import threading
import logging

log = logging.getLogger(__name__)

try:
    from PIL import Image, ImageDraw, ImageFont
    import pystray
    from pystray import MenuItem, Menu
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False
    log.warning("pystray/Pillow not available; tray icon disabled")


def _create_basketball_icon(size: int = 64) -> "Image.Image":
    """Generate a simple basketball icon programmatically."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Orange circle
    margin = 2
    draw.ellipse([margin, margin, size - margin, size - margin],
                 fill="#FF6B00", outline="#CC5500", width=2)

    # Lines on ball
    mid = size // 2
    draw.line([(mid, margin + 2), (mid, size - margin - 2)],
              fill="#CC5500", width=2)
    draw.line([(margin + 2, mid), (size - margin - 2, mid)],
              fill="#CC5500", width=2)

    # Curved lines (simplified as arcs)
    offset = size // 4
    draw.arc([margin - offset, margin, mid + offset, size - margin],
             start=300, end=60, fill="#CC5500", width=2)
    draw.arc([mid - offset, margin, size - margin + offset, size - margin],
             start=120, end=240, fill="#CC5500", width=2)

    return img


class TrayIcon:
    """Manages the Windows system tray icon."""

    def __init__(self, on_open, on_ticker, on_settings, on_quit):
        self._on_open = on_open
        self._on_ticker = on_ticker
        self._on_settings = on_settings
        self._on_quit = on_quit
        self._icon = None
        self._thread = None

    def start(self):
        if not HAS_TRAY:
            log.warning("Cannot start tray icon: pystray not available")
            return

        icon_image = _create_basketball_icon()

        menu = Menu(
            MenuItem("Open Tracker", self._handle_open, default=True),
            MenuItem("Toggle Ticker", self._handle_ticker),
            MenuItem("Settings", self._handle_settings),
            pystray.Menu.SEPARATOR,
            MenuItem("Quit", self._handle_quit),
        )

        self._icon = pystray.Icon(
            name="MarchMadness",
            icon=icon_image,
            title="March Madness Tracker",
            menu=menu,
        )

        self._thread = threading.Thread(target=self._icon.run, daemon=True,
                                        name="TrayIcon")
        self._thread.start()
        log.info("Tray icon started")

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def update_tooltip(self, text: str):
        if self._icon:
            self._icon.title = text

    # ── Handlers (run on tray thread, schedule to main) ────────────────────
    def _handle_open(self, icon=None, item=None):
        self._on_open()

    def _handle_ticker(self, icon=None, item=None):
        self._on_ticker()

    def _handle_settings(self, icon=None, item=None):
        self._on_settings()

    def _handle_quit(self, icon=None, item=None):
        self._on_quit()
