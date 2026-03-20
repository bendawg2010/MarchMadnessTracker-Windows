using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MarchMadnessTracker.Models;
using MarchMadnessTracker.Services;
using System.Collections.ObjectModel;
using System.Windows;

namespace MarchMadnessTracker.ViewModels;

public partial class MainViewModel : ObservableObject
{
    private readonly ScorePoller _poller;
    private readonly SettingsService _settingsService;

    [ObservableProperty]
    private int _selectedTabIndex;

    [ObservableProperty]
    private string _statusText = "Connecting...";

    [ObservableProperty]
    private bool _isLoading = true;

    public ScoresViewModel ScoresVM { get; }
    public BracketViewModel BracketVM { get; }
    public ScheduleViewModel ScheduleVM { get; }
    public SettingsViewModel SettingsVM { get; }

    public MainViewModel(
        ScorePoller poller,
        SettingsService settingsService,
        ScoresViewModel scoresVm,
        BracketViewModel bracketVm,
        ScheduleViewModel scheduleVm,
        SettingsViewModel settingsVm)
    {
        _poller = poller;
        _settingsService = settingsService;
        ScoresVM = scoresVm;
        BracketVM = bracketVm;
        ScheduleVM = scheduleVm;
        SettingsVM = settingsVm;

        _poller.ScoresUpdated += OnScoresUpdated;
        _poller.ErrorOccurred += OnError;
    }

    private void OnScoresUpdated(List<GameData> games)
    {
        Application.Current?.Dispatcher.Invoke(() =>
        {
            IsLoading = false;
            var liveCount = games.Count(g => g.State == GameState.In);
            var totalCount = games.Count;
            StatusText = liveCount > 0
                ? $"{liveCount} live game{(liveCount != 1 ? "s" : "")} | {totalCount} total"
                : $"{totalCount} games today";

            ScoresVM.UpdateScores(games);
            BracketVM.UpdateBracket(games);
            ScheduleVM.UpdateSchedule(games);
        });
    }

    private void OnError(string message)
    {
        Application.Current?.Dispatcher.Invoke(() =>
        {
            StatusText = $"Error: {message}";
        });
    }

    [RelayCommand]
    private void Quit()
    {
        if (Application.Current is App app)
        {
            app.QuitApplication();
        }
    }
}
