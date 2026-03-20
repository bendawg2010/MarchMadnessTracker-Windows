namespace MarchMadnessTracker.Models;

public class AppSettings
{
    public string FavoriteTeam { get; set; } = string.Empty;
    public bool NotificationsEnabled { get; set; } = true;
    public bool CloseGameAlerts { get; set; } = true;
    public bool UpsetAlerts { get; set; } = true;
    public bool FavoriteTeamAlerts { get; set; } = true;
    public bool TickerEnabled { get; set; } = false;
    public int LivePollingIntervalMs { get; set; } = 3000;
    public int IdlePollingIntervalMs { get; set; } = 20000;
}
