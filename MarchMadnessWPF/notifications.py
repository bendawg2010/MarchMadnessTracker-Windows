"""Windows toast notifications with graceful fallback."""

import logging
import threading

log = logging.getLogger(__name__)

_notifier = None
_backend = None


def _init_backend():
    """Try available notification backends."""
    global _notifier, _backend

    # Try plyer first
    try:
        from plyer import notification as plyer_notif
        _notifier = plyer_notif
        _backend = "plyer"
        log.info("Using plyer for notifications")
        return
    except ImportError:
        pass

    # Try win10toast
    try:
        from win10toast import ToastNotifier
        _notifier = ToastNotifier()
        _backend = "win10toast"
        log.info("Using win10toast for notifications")
        return
    except ImportError:
        pass

    log.warning("No notification backend available; notifications disabled")
    _backend = "none"


def notify(title: str, message: str, timeout: int = 5):
    """Send a Windows toast notification (non-blocking)."""
    if _backend is None:
        _init_backend()

    def _send():
        try:
            if _backend == "plyer":
                _notifier.notify(
                    title=title,
                    message=message,
                    app_name="March Madness Tracker",
                    timeout=timeout,
                )
            elif _backend == "win10toast":
                _notifier.show_toast(
                    title, message,
                    duration=timeout,
                    threaded=True,
                )
            else:
                log.debug("Notification (no backend): %s - %s", title, message)
        except Exception as e:
            log.debug("Notification error: %s", e)

    threading.Thread(target=_send, daemon=True).start()


def notify_close_game(game):
    """Send notification for a close game."""
    if game.home and game.away:
        title = "Close Game Alert!"
        msg = (f"{game.away.abbrev} {game.away.score} - "
               f"{game.home.abbrev} {game.home.score}  |  {game.short_detail}")
        if game.is_upset:
            title = "Upset Alert!"
        notify(title, msg)
