using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Threading;
using MarchMadnessTracker.Models;
using MarchMadnessTracker.Services;
using Microsoft.Extensions.DependencyInjection;

namespace MarchMadnessTracker.Views;

public partial class TickerWindow : Window
{
    private readonly DispatcherTimer _animationTimer;
    private double _tickerPosition;
    private double _tickerTextWidth;
    private ScorePoller? _poller;

    public TickerWindow()
    {
        InitializeComponent();

        // Position at top of screen, full width
        var workArea = SystemParameters.WorkArea;
        Left = 0;
        Top = 0;
        Width = SystemParameters.PrimaryScreenWidth;

        _animationTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(30)
        };
        _animationTimer.Tick += AnimateTicker;

        Loaded += TickerWindow_Loaded;
    }

    private void TickerWindow_Loaded(object sender, RoutedEventArgs e)
    {
        if (Application.Current is App app)
        {
            _poller = app.Services.GetService<ScorePoller>();
            if (_poller != null)
            {
                _poller.ScoresUpdated += OnScoresUpdated;
                UpdateTickerText(_poller.LatestScores);
            }
        }

        _tickerPosition = TickerCanvas.ActualWidth;
        _animationTimer.Start();
    }

    private void OnScoresUpdated(List<GameData> games)
    {
        Dispatcher.Invoke(() => UpdateTickerText(games));
    }

    private void UpdateTickerText(List<GameData> games)
    {
        if (games.Count == 0)
        {
            TickerText.Text = "No games scheduled. Check back during tournament time!";
            return;
        }

        var parts = new List<string>();
        foreach (var game in games)
        {
            string entry;
            switch (game.State)
            {
                case GameState.In:
                    entry = $"[LIVE] {game.AwaySeed} {game.AwayAbbreviation} {game.AwayScore} - {game.HomeSeed} {game.HomeAbbreviation} {game.HomeScore} ({game.TimeDisplay})";
                    if (game.IsUpset) entry += " *UPSET*";
                    break;
                case GameState.Post:
                    var winner = game.HomeScore > game.AwayScore ? game.HomeAbbreviation : game.AwayAbbreviation;
                    entry = $"[FINAL] {game.AwayAbbreviation} {game.AwayScore} - {game.HomeAbbreviation} {game.HomeScore}";
                    if (game.IsUpset) entry += " *UPSET*";
                    break;
                default:
                    entry = $"[{game.TimeDisplay}] {game.AwayAbbreviation} vs {game.HomeAbbreviation}";
                    break;
            }
            parts.Add(entry);
        }

        TickerText.Text = string.Join("     |     ", parts);

        // Measure text width
        TickerText.Measure(new Size(double.PositiveInfinity, double.PositiveInfinity));
        _tickerTextWidth = TickerText.DesiredSize.Width;
    }

    private void AnimateTicker(object? sender, EventArgs e)
    {
        _tickerPosition -= 1.5; // scroll speed

        if (_tickerPosition < -_tickerTextWidth)
        {
            _tickerPosition = TickerCanvas.ActualWidth;
        }

        Canvas.SetLeft(TickerText, _tickerPosition);
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
        _animationTimer.Stop();
        if (_poller != null)
        {
            _poller.ScoresUpdated -= OnScoresUpdated;
        }
        Close();
    }

    protected override void OnClosed(EventArgs e)
    {
        _animationTimer.Stop();
        if (_poller != null)
        {
            _poller.ScoresUpdated -= OnScoresUpdated;
        }
        base.OnClosed(e);
    }
}
