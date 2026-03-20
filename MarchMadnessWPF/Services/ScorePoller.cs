using MarchMadnessTracker.Models;

namespace MarchMadnessTracker.Services;

public class ScorePoller
{
    private readonly EspnService _espnService;
    private readonly SettingsService _settingsService;
    private readonly NotificationService _notificationService;
    private System.Threading.Timer? _timer;
    private bool _isRunning;
    private readonly HashSet<string> _notifiedGames = new();

    public event Action<List<GameData>>? ScoresUpdated;
    public event Action<string>? ErrorOccurred;

    public List<GameData> LatestScores { get; private set; } = new();
    public bool HasLiveGames => LatestScores.Any(g => g.State == GameState.In);

    public ScorePoller(EspnService espnService, SettingsService settingsService, NotificationService notificationService)
    {
        _espnService = espnService;
        _settingsService = settingsService;
        _notificationService = notificationService;
    }

    public void Start()
    {
        if (_isRunning) return;
        _isRunning = true;

        // Initial fetch
        _ = PollAsync();

        // Set up timer
        var interval = _settingsService.Settings.IdlePollingIntervalMs;
        _timer = new System.Threading.Timer(
            async _ => await PollAsync(),
            null,
            interval,
            interval);
    }

    public void Stop()
    {
        _isRunning = false;
        _timer?.Dispose();
        _timer = null;
    }

    private async Task PollAsync()
    {
        try
        {
            var scores = await _espnService.FetchScoresAsync();
            if (scores.Count > 0)
            {
                var previousScores = LatestScores;
                LatestScores = scores;

                // Check for notifications
                CheckNotifications(scores, previousScores);

                ScoresUpdated?.Invoke(scores);

                // Adjust polling interval
                AdjustPollingInterval();
            }
        }
        catch (Exception ex)
        {
            ErrorOccurred?.Invoke(ex.Message);
        }
    }

    private void CheckNotifications(List<GameData> current, List<GameData> previous)
    {
        var settings = _settingsService.Settings;
        if (!settings.NotificationsEnabled) return;

        foreach (var game in current)
        {
            // Close game alert
            if (settings.CloseGameAlerts && game.ShouldNotify)
            {
                var key = $"close_{game.GameId}_{game.Period}";
                if (!_notifiedGames.Contains(key))
                {
                    _notifiedGames.Add(key);
                    _notificationService.ShowNotification(
                        "Close Game Alert!",
                        $"{game.AwayAbbreviation} {game.AwayScore} - {game.HomeAbbreviation} {game.HomeScore} | {game.TimeDisplay}");
                }
            }

            // Upset detection
            if (settings.UpsetAlerts && game.IsUpset && game.State == GameState.Post)
            {
                var key = $"upset_{game.GameId}";
                if (!_notifiedGames.Contains(key))
                {
                    _notifiedGames.Add(key);
                    var winner = game.HomeScore > game.AwayScore ? game.HomeAbbreviation : game.AwayAbbreviation;
                    var loser = game.HomeScore > game.AwayScore ? game.AwayAbbreviation : game.HomeAbbreviation;
                    _notificationService.ShowNotification(
                        "UPSET!",
                        $"{winner} defeats {loser}! {game.AwayScore}-{game.HomeScore}");
                }
            }

            // Favorite team
            if (settings.FavoriteTeamAlerts && !string.IsNullOrEmpty(settings.FavoriteTeam))
            {
                if ((game.HomeAbbreviation == settings.FavoriteTeam || game.AwayAbbreviation == settings.FavoriteTeam)
                    && game.State == GameState.Post)
                {
                    var key = $"fav_{game.GameId}";
                    if (!_notifiedGames.Contains(key))
                    {
                        _notifiedGames.Add(key);
                        _notificationService.ShowNotification(
                            $"{settings.FavoriteTeam} Game Final",
                            $"{game.AwayAbbreviation} {game.AwayScore} - {game.HomeAbbreviation} {game.HomeScore}");
                    }
                }
            }
        }
    }

    private void AdjustPollingInterval()
    {
        if (_timer == null) return;

        var interval = HasLiveGames
            ? _settingsService.Settings.LivePollingIntervalMs
            : _settingsService.Settings.IdlePollingIntervalMs;

        _timer.Change(interval, interval);
    }
}
