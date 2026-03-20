# March Madness Tracker - Windows

A Windows system tray application that tracks NCAA March Madness tournament scores in real time using the ESPN API. Available in two versions: a lightweight Python version and a full WPF (.NET 8) app.

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue) ![.NET](https://img.shields.io/badge/.NET-8.0-purple) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **System tray icon** with basketball icon; click to open the main window
- **Tabbed interface**: Scores, Bracket, Schedule
- **Live score polling**: 3-second updates during live games, 20-second idle polling
- **Floating score widgets**: pop out any game into a small always-on-top window
- **Scrolling ticker bar**: borderless overlay at the top of the screen
- **Upset detection**: highlights when a lower seed is winning
- **Close game alerts**: Windows toast notifications when games are within 5 points in the 2nd half
- **Dark theme** UI with team color accents
- **Settings**: favorite team, notification toggle, ticker size

## Installation

### Option A: WPF App (.NET 8) - Recommended

**Requirements:** [.NET 8 Runtime](https://dotnet.microsoft.com/download/dotnet/8.0) or SDK

```bash
cd MarchMadnessWPF
dotnet run
```

To build a standalone .exe:
```bash
cd MarchMadnessWPF
dotnet publish -c Release -r win-x64 --self-contained
```
The executable will be at `bin/Release/net8.0-windows/win-x64/publish/MarchMadnessTracker.exe`.

### Option B: Python Version - Lightweight

**Requirements:** Python 3.10+, Windows 10/11

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python main.py
```

## Dependencies

| Package    | Purpose                    |
|------------|----------------------------|
| requests   | ESPN API HTTP calls        |
| Pillow     | Image handling, tray icon  |
| pystray    | Windows system tray icon   |
| plyer      | Toast notifications        |
| pyinstaller| Build standalone .exe      |

## Build Standalone .exe

Double-click `build.bat` or run from a terminal:

```bash
build.bat
```

The executable will be created at `dist/MarchMadnessTracker.exe`.

## ESPN API

All data comes from the public ESPN scoreboard API:

```
https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=100
```

- `groups=100` filters to NCAA Tournament games
- Add `&dates=YYYYMMDD` for a specific date

## File Structure

```
MarchMadnessTracker-Windows/
├── main.py                 # Entry point & app controller
├── espn_api.py             # ESPN API client & data models
├── score_poller.py         # Background polling thread
├── tray_icon.py            # System tray (pystray)
├── notifications.py        # Windows toast notifications
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Main tabbed window
│   ├── scores_tab.py       # Live scores list
│   ├── bracket_tab.py      # Tournament bracket by round
│   ├── schedule_tab.py     # Date-based schedule
│   ├── ticker_bar.py       # Floating scrolling ticker
│   ├── score_widget.py     # Pop-out game widget
│   ├── settings_window.py  # Settings dialog
│   └── styles.py           # Dark theme colors & fonts
├── requirements.txt
├── build.bat               # PyInstaller build script
└── README.md
```

## Usage Tips

- **Right-click** the tray icon for the menu (Open, Ticker, Settings, Quit)
- **Double-click** the tray icon to open the main window
- Click the **arrow icon** on any game card to pop it out as a floating widget
- The **ticker bar** can be dragged to reposition; right-click to close
- Score widgets are always-on-top and draggable
- Settings are saved to `~/.marchmadness_settings.json`
