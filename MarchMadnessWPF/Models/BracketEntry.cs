namespace MarchMadnessTracker.Models;

public class BracketEntry
{
    public string Region { get; set; } = string.Empty;
    public string Round { get; set; } = string.Empty;
    public int RoundNumber { get; set; }
    public GameData Game { get; set; } = new();
}

public static class TournamentRounds
{
    public const string Round64 = "Round of 64";
    public const string Round32 = "Round of 32";
    public const string Sweet16 = "Sweet 16";
    public const string Elite8 = "Elite Eight";
    public const string FinalFour = "Final Four";
    public const string Championship = "Championship";

    public static readonly string[] AllRounds =
    {
        Round64, Round32, Sweet16, Elite8, FinalFour, Championship
    };

    public static int GetRoundNumber(string roundName)
    {
        return roundName.ToLowerInvariant() switch
        {
            var r when r.Contains("64") || r.Contains("first round") => 1,
            var r when r.Contains("32") || r.Contains("second round") => 2,
            var r when r.Contains("sweet") || r.Contains("regional semi") => 3,
            var r when r.Contains("elite") || r.Contains("regional final") => 4,
            var r when r.Contains("final four") || r.Contains("national semi") => 5,
            var r when r.Contains("championship") || r.Contains("national championship") => 6,
            _ => 0
        };
    }
}
