using System.Net.Http;
using System.Text.Json;
using MarchMadnessTracker.Models;

namespace MarchMadnessTracker.Services;

public class EspnService
{
    private const string ScoreboardUrl =
        "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=100";

    private readonly HttpClient _httpClient;

    public EspnService()
    {
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("User-Agent", "MarchMadnessTracker/1.0");
        _httpClient.Timeout = TimeSpan.FromSeconds(10);
    }

    public async Task<List<GameData>> FetchScoresAsync()
    {
        try
        {
            var json = await _httpClient.GetStringAsync(ScoreboardUrl);
            return ParseScoreboard(json);
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"ESPN API error: {ex.Message}");
            return new List<GameData>();
        }
    }

    private List<GameData> ParseScoreboard(string json)
    {
        var games = new List<GameData>();

        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        if (!root.TryGetProperty("events", out var events))
            return games;

        foreach (var evt in events.EnumerateArray())
        {
            try
            {
                var game = ParseEvent(evt);
                if (game != null)
                    games.Add(game);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error parsing event: {ex.Message}");
            }
        }

        return games;
    }

    private GameData? ParseEvent(JsonElement evt)
    {
        var game = new GameData();

        game.GameId = evt.GetProperty("id").GetString() ?? string.Empty;

        if (evt.TryGetProperty("date", out var dateEl))
        {
            if (DateTime.TryParse(dateEl.GetString(), out var dt))
                game.StartTime = dt;
        }

        var competitions = evt.GetProperty("competitions");
        if (competitions.GetArrayLength() == 0) return null;

        var competition = competitions[0];
        var competitors = competition.GetProperty("competitors");

        foreach (var competitor in competitors.EnumerateArray())
        {
            var homeAway = competitor.GetProperty("homeAway").GetString();
            var team = competitor.GetProperty("team");

            var abbreviation = GetStringProp(team, "abbreviation", "???");
            var displayName = GetStringProp(team, "displayName", abbreviation);
            var color = GetStringProp(team, "color", "333333");
            var logo = string.Empty;

            if (team.TryGetProperty("logo", out var logoEl))
                logo = logoEl.GetString() ?? string.Empty;

            var score = 0;
            if (competitor.TryGetProperty("score", out var scoreEl))
            {
                var scoreStr = scoreEl.GetString() ?? "0";
                int.TryParse(scoreStr, out score);
            }

            var seed = 0;
            if (competitor.TryGetProperty("curatedRank", out var rank))
            {
                if (rank.TryGetProperty("current", out var currentRank))
                    seed = currentRank.GetInt32();
            }

            if (homeAway == "home")
            {
                game.HomeTeam = displayName;
                game.HomeAbbreviation = abbreviation;
                game.HomeScore = score;
                game.HomeSeed = seed;
                game.HomeColor = $"#{color}";
                game.HomeLogo = logo;
            }
            else
            {
                game.AwayTeam = displayName;
                game.AwayAbbreviation = abbreviation;
                game.AwayScore = score;
                game.AwaySeed = seed;
                game.AwayColor = $"#{color}";
                game.AwayLogo = logo;
            }
        }

        // Status
        if (evt.TryGetProperty("status", out var status))
        {
            if (status.TryGetProperty("type", out var statusType))
            {
                var state = GetStringProp(statusType, "state", "pre");
                game.State = state switch
                {
                    "in" => GameState.In,
                    "post" => GameState.Post,
                    _ => GameState.Pre
                };

                if (statusType.TryGetProperty("detail", out var detail))
                    game.StatusDetail = detail.GetString() ?? string.Empty;
            }

            if (status.TryGetProperty("displayClock", out var clock))
                game.DisplayClock = clock.GetString() ?? string.Empty;

            if (status.TryGetProperty("period", out var period))
                game.Period = period.GetInt32();
        }

        // Notes (round info)
        if (competition.TryGetProperty("notes", out var notes) && notes.GetArrayLength() > 0)
        {
            var note = notes[0];
            if (note.TryGetProperty("headline", out var headline))
            {
                game.Headline = headline.GetString() ?? string.Empty;
                game.RoundInfo = game.Headline;
            }
        }

        // Broadcast
        if (competition.TryGetProperty("broadcasts", out var broadcasts) && broadcasts.GetArrayLength() > 0)
        {
            var broadcast = broadcasts[0];
            if (broadcast.TryGetProperty("names", out var names) && names.GetArrayLength() > 0)
            {
                game.Broadcast = names[0].GetString() ?? string.Empty;
            }
        }

        return game;
    }

    private static string GetStringProp(JsonElement el, string prop, string defaultValue)
    {
        return el.TryGetProperty(prop, out var val) ? val.GetString() ?? defaultValue : defaultValue;
    }
}
