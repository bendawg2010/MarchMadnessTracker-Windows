# March Madness Tracker - Windows (WPF)

A Windows desktop application for tracking NCAA March Madness tournament scores in real time. Lives in the system tray with a basketball icon and provides live score updates, floating score widgets, and desktop notifications.

## Requirements

- Windows 10/11
- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)

## Build

```bash
cd MarchMadnessWPF
dotnet build
```

## Run

```bash
dotnet run
```

## Publish (standalone .exe)

```bash
# Framework-dependent (small, requires .NET 8 runtime)
dotnet publish -c Release

# Self-contained (larger, no runtime needed)
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

The output will be in `bin/Release/net8.0-windows/publish/`.

## Features

- **System tray icon** - basketball icon, click to open main window
- **Live scores** from ESPN public API (NCAA Tournament games)
- **Three tabs**: Scores, Bracket, Schedule
- **Auto-polling**: Every 3 seconds during live games, every 20 seconds when idle
- **Floating score widgets**: Click any game card to detach it as an always-on-top mini window
- **Scrolling ticker bar**: Optional score ticker at top of screen
- **Upset detection**: Orange highlight when a lower-seeded team is winning or has won
- **Desktop notifications**: Alerts for close games (within 5 points in last 5 minutes)
- **Settings**: Favorite team selection, notification preferences, ticker toggle
- **Dark theme**: Modern dark UI with Material Design-inspired styling

## Architecture

```
MarchMadnessWPF/
  App.xaml / App.xaml.cs          - Application entry, tray icon, DI setup
  MainWindow.xaml / .cs           - Main popup window with tabs
  Models/
    GameData.cs                   - Game data model
    AppSettings.cs                - Settings model
    BracketEntry.cs               - Bracket/round data
  Services/
    EspnService.cs                - ESPN API client
    ScorePoller.cs                - Polling timer with adaptive intervals
    NotificationService.cs        - Desktop notification popups
    SettingsService.cs            - JSON settings persistence
  ViewModels/
    MainViewModel.cs              - Main window VM
    ScoresViewModel.cs            - Scores tab VM with floating window management
    BracketViewModel.cs           - Bracket tab VM with region/round grouping
    ScheduleViewModel.cs          - Schedule tab VM with date grouping
    SettingsViewModel.cs          - Settings tab VM
  Views/
    ScoresView.xaml / .cs         - Scores tab (live, completed, upcoming)
    BracketView.xaml / .cs        - Bracket tab (by region)
    ScheduleView.xaml / .cs       - Schedule tab (by date)
    SettingsView.xaml / .cs       - Settings tab
    FloatingScoreWindow.xaml / .cs - Detachable always-on-top score widget
    NotificationWindow.xaml / .cs - Toast-style notification popup
    TickerWindow.xaml / .cs       - Scrolling score ticker bar
  Converters/
    Converters.cs                 - Value converters for data binding
  Resources/
    Styles.xaml                   - Dark theme styles and colors
```

## Data Source

Uses the ESPN public API endpoint:
```
https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=100
```

The `groups=100` parameter filters for NCAA Tournament games only.
