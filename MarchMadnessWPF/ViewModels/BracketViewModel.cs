using CommunityToolkit.Mvvm.ComponentModel;
using MarchMadnessTracker.Models;
using System.Collections.ObjectModel;

namespace MarchMadnessTracker.ViewModels;

public partial class BracketViewModel : ObservableObject
{
    [ObservableProperty]
    private ObservableCollection<BracketRegionGroup> _regions = new();

    [ObservableProperty]
    private string _selectedRoundFilter = "All Rounds";

    public List<string> RoundFilters { get; } = new()
    {
        "All Rounds",
        "Round of 64",
        "Round of 32",
        "Sweet 16",
        "Elite Eight",
        "Final Four",
        "Championship"
    };

    partial void OnSelectedRoundFilterChanged(string value)
    {
        if (_cachedGames.Count > 0)
            UpdateBracket(_cachedGames);
    }

    private List<GameData> _cachedGames = new();

    public void UpdateBracket(List<GameData> games)
    {
        _cachedGames = games;

        var entries = games.Select(g => new BracketEntry
        {
            Region = ExtractRegion(g.Headline),
            Round = ExtractRound(g.Headline),
            RoundNumber = TournamentRounds.GetRoundNumber(g.Headline),
            Game = g
        }).ToList();

        // Apply round filter
        if (SelectedRoundFilter != "All Rounds")
        {
            var filterRound = TournamentRounds.GetRoundNumber(SelectedRoundFilter);
            entries = entries.Where(e => e.RoundNumber == filterRound).ToList();
        }

        var grouped = entries
            .GroupBy(e => string.IsNullOrEmpty(e.Region) ? "Tournament" : e.Region)
            .Select(g => new BracketRegionGroup
            {
                RegionName = g.Key,
                Games = new ObservableCollection<BracketEntry>(
                    g.OrderBy(e => e.RoundNumber).ThenBy(e => e.Game.StartTime))
            })
            .OrderBy(g => g.RegionName)
            .ToList();

        Regions = new ObservableCollection<BracketRegionGroup>(grouped);
    }

    private static string ExtractRegion(string headline)
    {
        if (string.IsNullOrEmpty(headline)) return string.Empty;

        var regions = new[] { "East", "West", "South", "Midwest", "North", "Southeast", "Southwest" };
        foreach (var region in regions)
        {
            if (headline.Contains(region, StringComparison.OrdinalIgnoreCase))
                return region;
        }

        if (headline.Contains("Final Four", StringComparison.OrdinalIgnoreCase) ||
            headline.Contains("Championship", StringComparison.OrdinalIgnoreCase) ||
            headline.Contains("National", StringComparison.OrdinalIgnoreCase))
            return "Final Four";

        return string.Empty;
    }

    private static string ExtractRound(string headline)
    {
        if (string.IsNullOrEmpty(headline)) return string.Empty;

        var roundNames = new[]
        {
            ("64", "Round of 64"),
            ("First Round", "Round of 64"),
            ("32", "Round of 32"),
            ("Second Round", "Round of 32"),
            ("Sweet", "Sweet 16"),
            ("Elite", "Elite Eight"),
            ("Final Four", "Final Four"),
            ("National Semi", "Final Four"),
            ("Championship", "Championship"),
            ("National Championship", "Championship")
        };

        foreach (var (key, name) in roundNames)
        {
            if (headline.Contains(key, StringComparison.OrdinalIgnoreCase))
                return name;
        }

        return headline;
    }
}

public class BracketRegionGroup
{
    public string RegionName { get; set; } = string.Empty;
    public ObservableCollection<BracketEntry> Games { get; set; } = new();
}
