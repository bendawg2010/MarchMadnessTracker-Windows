using CommunityToolkit.Mvvm.ComponentModel;
using MarchMadnessTracker.Models;
using System.Collections.ObjectModel;

namespace MarchMadnessTracker.ViewModels;

public partial class ScheduleViewModel : ObservableObject
{
    [ObservableProperty]
    private ObservableCollection<ScheduleGroup> _scheduleGroups = new();

    [ObservableProperty]
    private string _summary = string.Empty;

    public void UpdateSchedule(List<GameData> games)
    {
        var groups = games
            .GroupBy(g => g.StartTime.ToLocalTime().Date)
            .OrderBy(g => g.Key)
            .Select(g => new ScheduleGroup
            {
                Date = g.Key,
                DateDisplay = g.Key.Date == DateTime.Today ? "Today"
                    : g.Key.Date == DateTime.Today.AddDays(1) ? "Tomorrow"
                    : g.Key.ToString("dddd, MMM d"),
                Games = new ObservableCollection<GameData>(
                    g.OrderBy(game => game.StartTime))
            })
            .ToList();

        ScheduleGroups = new ObservableCollection<ScheduleGroup>(groups);

        var total = games.Count;
        var live = games.Count(g => g.State == GameState.In);
        var done = games.Count(g => g.State == GameState.Post);
        var upcoming = games.Count(g => g.State == GameState.Pre);

        Summary = $"{total} games: {live} live, {done} completed, {upcoming} upcoming";
    }
}

public class ScheduleGroup
{
    public DateTime Date { get; set; }
    public string DateDisplay { get; set; } = string.Empty;
    public ObservableCollection<GameData> Games { get; set; } = new();
}
