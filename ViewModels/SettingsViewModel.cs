using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MarchMadnessTracker.Services;

namespace MarchMadnessTracker.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    private readonly SettingsService _settingsService;

    [ObservableProperty]
    private string _favoriteTeam;

    [ObservableProperty]
    private bool _notificationsEnabled;

    [ObservableProperty]
    private bool _closeGameAlerts;

    [ObservableProperty]
    private bool _upsetAlerts;

    [ObservableProperty]
    private bool _favoriteTeamAlerts;

    [ObservableProperty]
    private bool _tickerEnabled;

    [ObservableProperty]
    private string _statusMessage = string.Empty;

    public List<string> CommonTeams { get; } = new()
    {
        "", "DUKE", "UNC", "KANS", "GONZ", "BAYLOR", "UK", "CONN", "HOU",
        "ARIZ", "PURDUE", "TENN", "MARQ", "ALA", "CREIGH", "XAVIER",
        "SDSU", "MICH", "MSU", "UCLA", "IU", "UVA", "IOWA", "TXAM",
        "AUB", "PITT", "ISU", "WVU", "COLO", "BYU", "FLA", "ORE",
        "WAKE", "CLEM", "NEB", "OKLA", "ARK", "WISC", "ILL", "OHST"
    };

    public SettingsViewModel(SettingsService settingsService)
    {
        _settingsService = settingsService;
        var s = settingsService.Settings;
        _favoriteTeam = s.FavoriteTeam;
        _notificationsEnabled = s.NotificationsEnabled;
        _closeGameAlerts = s.CloseGameAlerts;
        _upsetAlerts = s.UpsetAlerts;
        _favoriteTeamAlerts = s.FavoriteTeamAlerts;
        _tickerEnabled = s.TickerEnabled;
    }

    [RelayCommand]
    private void Save()
    {
        _settingsService.UpdateSettings(s =>
        {
            s.FavoriteTeam = FavoriteTeam;
            s.NotificationsEnabled = NotificationsEnabled;
            s.CloseGameAlerts = CloseGameAlerts;
            s.UpsetAlerts = UpsetAlerts;
            s.FavoriteTeamAlerts = FavoriteTeamAlerts;
            s.TickerEnabled = TickerEnabled;
        });

        StatusMessage = "Settings saved!";

        // Handle ticker
        if (TickerEnabled)
        {
            ShowTicker();
        }
        else
        {
            HideTicker();
        }

        // Clear status after delay
        _ = ClearStatusAsync();
    }

    private async Task ClearStatusAsync()
    {
        await Task.Delay(2000);
        StatusMessage = string.Empty;
    }

    private void ShowTicker()
    {
        System.Windows.Application.Current?.Dispatcher.Invoke(() =>
        {
            var existing = System.Windows.Application.Current.Windows
                .OfType<Views.TickerWindow>()
                .FirstOrDefault();

            if (existing == null)
            {
                var ticker = new Views.TickerWindow();
                ticker.Show();
            }
        });
    }

    private void HideTicker()
    {
        System.Windows.Application.Current?.Dispatcher.Invoke(() =>
        {
            var existing = System.Windows.Application.Current.Windows
                .OfType<Views.TickerWindow>()
                .FirstOrDefault();

            existing?.Close();
        });
    }
}
