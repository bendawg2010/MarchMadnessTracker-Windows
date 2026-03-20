using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MarchMadnessTracker.Models;
using MarchMadnessTracker.Views;
using System.Collections.ObjectModel;
using System.Windows;

namespace MarchMadnessTracker.ViewModels;

public partial class ScoresViewModel : ObservableObject
{
    [ObservableProperty]
    private ObservableCollection<GameData> _liveGames = new();

    [ObservableProperty]
    private ObservableCollection<GameData> _completedGames = new();

    [ObservableProperty]
    private ObservableCollection<GameData> _upcomingGames = new();

    [ObservableProperty]
    private string _filterText = string.Empty;

    private List<GameData> _allGames = new();
    private readonly List<FloatingScoreWindow> _floatingWindows = new();

    public void UpdateScores(List<GameData> games)
    {
        _allGames = games;
        ApplyFilter();
    }

    partial void OnFilterTextChanged(string value)
    {
        ApplyFilter();
    }

    private void ApplyFilter()
    {
        var filtered = string.IsNullOrWhiteSpace(FilterText)
            ? _allGames
            : _allGames.Where(g =>
                g.HomeTeam.Contains(FilterText, StringComparison.OrdinalIgnoreCase) ||
                g.AwayTeam.Contains(FilterText, StringComparison.OrdinalIgnoreCase) ||
                g.HomeAbbreviation.Contains(FilterText, StringComparison.OrdinalIgnoreCase) ||
                g.AwayAbbreviation.Contains(FilterText, StringComparison.OrdinalIgnoreCase))
            .ToList();

        LiveGames = new ObservableCollection<GameData>(
            filtered.Where(g => g.State == GameState.In)
                    .OrderBy(g => g.DisplayClock));

        CompletedGames = new ObservableCollection<GameData>(
            filtered.Where(g => g.State == GameState.Post));

        UpcomingGames = new ObservableCollection<GameData>(
            filtered.Where(g => g.State == GameState.Pre)
                    .OrderBy(g => g.StartTime));

        // Update floating windows
        UpdateFloatingWindows();
    }

    [RelayCommand]
    private void DetachGame(GameData? game)
    {
        if (game == null) return;

        Application.Current?.Dispatcher.Invoke(() =>
        {
            // Check if already floating
            var existing = _floatingWindows.FirstOrDefault(w => w.GameId == game.GameId);
            if (existing != null)
            {
                existing.Activate();
                return;
            }

            var floatingWindow = new FloatingScoreWindow(game);
            floatingWindow.Closed += (s, e) =>
            {
                if (s is FloatingScoreWindow fw)
                    _floatingWindows.Remove(fw);
            };
            _floatingWindows.Add(floatingWindow);
            floatingWindow.Show();
        });
    }

    private void UpdateFloatingWindows()
    {
        foreach (var window in _floatingWindows.ToList())
        {
            var updated = _allGames.FirstOrDefault(g => g.GameId == window.GameId);
            if (updated != null)
            {
                window.UpdateGame(updated);
            }
        }
    }
}
