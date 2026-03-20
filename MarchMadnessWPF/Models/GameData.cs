namespace MarchMadnessTracker.Models;

public class GameData
{
    public string GameId { get; set; } = string.Empty;
    public string HomeTeam { get; set; } = string.Empty;
    public string AwayTeam { get; set; } = string.Empty;
    public string HomeAbbreviation { get; set; } = string.Empty;
    public string AwayAbbreviation { get; set; } = string.Empty;
    public int HomeScore { get; set; }
    public int AwayScore { get; set; }
    public int HomeSeed { get; set; }
    public int AwaySeed { get; set; }
    public string HomeColor { get; set; } = "#333333";
    public string AwayColor { get; set; } = "#333333";
    public string HomeLogo { get; set; } = string.Empty;
    public string AwayLogo { get; set; } = string.Empty;
    public GameState State { get; set; } = GameState.Pre;
    public string DisplayClock { get; set; } = string.Empty;
    public int Period { get; set; }
    public string StatusDetail { get; set; } = string.Empty;
    public string Headline { get; set; } = string.Empty;
    public string RoundInfo { get; set; } = string.Empty;
    public string Broadcast { get; set; } = string.Empty;
    public DateTime StartTime { get; set; }
    public bool IsUpset => State != GameState.Pre && GetLeadingTeamSeed() > GetTrailingTeamSeed() && GetLeadingTeamSeed() > 0 && GetTrailingTeamSeed() > 0;
    public bool IsCloseGame => State == GameState.In && Math.Abs(HomeScore - AwayScore) <= 5;

    public bool IsLastFiveMinutes
    {
        get
        {
            if (State != GameState.In) return false;
            if (Period < 2) return false;
            if (string.IsNullOrEmpty(DisplayClock)) return false;

            // Parse clock - format is "MM:SS" or "M:SS"
            var parts = DisplayClock.Split(':');
            if (parts.Length == 2 && int.TryParse(parts[0], out int minutes))
            {
                return minutes < 5;
            }
            return false;
        }
    }

    public bool ShouldNotify => IsCloseGame && IsLastFiveMinutes;

    private int GetLeadingTeamSeed()
    {
        return HomeScore >= AwayScore ? HomeSeed : AwaySeed;
    }

    private int GetTrailingTeamSeed()
    {
        return HomeScore >= AwayScore ? AwaySeed : HomeSeed;
    }

    public string ScoreDisplay => State == GameState.Pre
        ? "vs"
        : $"{AwayScore} - {HomeScore}";

    public string TimeDisplay => State switch
    {
        GameState.Pre => StartTime.ToLocalTime().ToString("h:mm tt"),
        GameState.Post => "FINAL",
        GameState.In => Period > 2 ? $"OT {DisplayClock}" : $"{GetPeriodName()} {DisplayClock}",
        _ => string.Empty
    };

    private string GetPeriodName() => Period switch
    {
        1 => "1st Half",
        2 => "2nd Half",
        _ => $"OT{Period - 2}"
    };
}

public enum GameState
{
    Pre,
    In,
    Post
}
