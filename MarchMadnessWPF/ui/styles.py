"""Dark theme colors, fonts, and style configuration."""

# ── Color Palette ──────────────────────────────────────────────────────────
BG_PRIMARY = "#1a1a2e"       # Deep navy background
BG_SECONDARY = "#16213e"     # Card / panel background
BG_TERTIARY = "#0f3460"      # Accent panels, hover
BG_INPUT = "#222244"         # Entry / input fields
ACCENT = "#e94560"           # March Madness red-orange
ACCENT_HOVER = "#ff6b81"
TEXT_PRIMARY = "#eaeaea"      # Main text
TEXT_SECONDARY = "#a0a0b8"   # Muted text
TEXT_DIM = "#606080"          # Very muted
LIVE_GREEN = "#00e676"        # Live indicator
FINAL_GRAY = "#888899"
UPSET_GOLD = "#ffd700"
BORDER = "#2a2a4a"
SCROLLBAR_BG = "#1a1a2e"
SCROLLBAR_FG = "#3a3a5a"

# ── Fonts ──────────────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_HEADING = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_SCORE = (FONT_FAMILY, 22, "bold")
FONT_TICKER = (FONT_FAMILY, 12, "bold")
FONT_SEED = (FONT_FAMILY, 9)
FONT_TAB = (FONT_FAMILY, 11, "bold")

# ── Dimensions ─────────────────────────────────────────────────────────────
MAIN_WIDTH = 520
MAIN_HEIGHT = 640
WIDGET_WIDTH = 280
WIDGET_HEIGHT = 110
TICKER_HEIGHT = 32
CARD_PAD_X = 10
CARD_PAD_Y = 6

# ── Status Labels ──────────────────────────────────────────────────────────
STATUS_COLORS = {
    "pre":  TEXT_SECONDARY,
    "in":   LIVE_GREEN,
    "post": FINAL_GRAY,
}


def apply_dark_theme(root):
    """Apply the dark theme to a tkinter root/Toplevel via ttk styles."""
    import tkinter.ttk as ttk

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG_PRIMARY, foreground=TEXT_PRIMARY,
                     font=FONT_BODY, borderwidth=0)
    style.configure("TFrame", background=BG_PRIMARY)
    style.configure("TLabel", background=BG_PRIMARY, foreground=TEXT_PRIMARY)
    style.configure("TButton", background=BG_TERTIARY, foreground=TEXT_PRIMARY,
                     padding=(12, 6), font=FONT_BODY_BOLD)
    style.map("TButton",
              background=[("active", ACCENT), ("pressed", ACCENT_HOVER)])
    style.configure("Accent.TButton", background=ACCENT, foreground="white",
                     font=FONT_BODY_BOLD)
    style.map("Accent.TButton",
              background=[("active", ACCENT_HOVER)])

    # Notebook (tabs)
    style.configure("TNotebook", background=BG_PRIMARY, borderwidth=0)
    style.configure("TNotebook.Tab", background=BG_SECONDARY,
                     foreground=TEXT_SECONDARY, padding=(16, 8),
                     font=FONT_TAB)
    style.map("TNotebook.Tab",
              background=[("selected", BG_TERTIARY)],
              foreground=[("selected", TEXT_PRIMARY)])

    # Entry
    style.configure("TEntry", fieldbackground=BG_INPUT, foreground=TEXT_PRIMARY,
                     insertcolor=TEXT_PRIMARY)

    # Scrollbar
    style.configure("Vertical.TScrollbar",
                     background=SCROLLBAR_FG, troughcolor=SCROLLBAR_BG,
                     borderwidth=0, arrowsize=0)

    # Checkbutton
    style.configure("TCheckbutton", background=BG_PRIMARY,
                     foreground=TEXT_PRIMARY, font=FONT_BODY)

    # Scale
    style.configure("TScale", background=BG_PRIMARY, troughcolor=BG_SECONDARY)

    # Card frame
    style.configure("Card.TFrame", background=BG_SECONDARY)
    style.configure("Card.TLabel", background=BG_SECONDARY,
                     foreground=TEXT_PRIMARY)
    style.configure("CardDim.TLabel", background=BG_SECONDARY,
                     foreground=TEXT_SECONDARY)
    style.configure("Live.TLabel", background=BG_SECONDARY,
                     foreground=LIVE_GREEN, font=FONT_SMALL)
    style.configure("Score.TLabel", background=BG_SECONDARY,
                     foreground=TEXT_PRIMARY, font=FONT_SCORE)
    style.configure("Seed.TLabel", background=BG_SECONDARY,
                     foreground=TEXT_DIM, font=FONT_SEED)
    style.configure("Upset.TLabel", background=BG_SECONDARY,
                     foreground=UPSET_GOLD, font=FONT_SMALL)

    return style
