using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using MarchMadnessTracker.Models;

namespace MarchMadnessTracker.Views;

public partial class FloatingScoreWindow : Window
{
    public string GameId { get; }

    public FloatingScoreWindow(GameData game)
    {
        InitializeComponent();
        GameId = game.GameId;
        UpdateGame(game);
    }

    public void UpdateGame(GameData game)
    {
        Dispatcher.Invoke(() =>
        {
            // Status
            switch (game.State)
            {
                case GameState.In:
                    StatusBadge.Background = new SolidColorBrush(Color.FromRgb(76, 175, 80));
                    StatusText.Text = "LIVE";
                    break;
                case GameState.Post:
                    StatusBadge.Background = new SolidColorBrush(Color.FromRgb(158, 158, 158));
                    StatusText.Text = "FINAL";
                    break;
                default:
                    StatusBadge.Background = new SolidColorBrush(Color.FromRgb(100, 181, 246));
                    StatusText.Text = "UPCOMING";
                    break;
            }

            ClockText.Text = game.TimeDisplay;

            // Away team
            AwayTeamText.Text = game.AwayAbbreviation;
            AwayScoreText.Text = game.State == GameState.Pre ? "" : game.AwayScore.ToString();
            if (game.AwaySeed > 0)
            {
                AwaySeedBorder.Visibility = Visibility.Visible;
                AwaySeedText.Text = game.AwaySeed.ToString();
                try
                {
                    var c = (Color)ColorConverter.ConvertFromString(game.AwayColor);
                    AwaySeedBorder.Background = new SolidColorBrush(Color.FromArgb(128, c.R, c.G, c.B));
                }
                catch { AwaySeedBorder.Background = new SolidColorBrush(Color.FromArgb(128, 51, 51, 51)); }
            }
            else
            {
                AwaySeedBorder.Visibility = Visibility.Collapsed;
            }

            // Home team
            HomeTeamText.Text = game.HomeAbbreviation;
            HomeScoreText.Text = game.State == GameState.Pre ? "" : game.HomeScore.ToString();
            if (game.HomeSeed > 0)
            {
                HomeSeedBorder.Visibility = Visibility.Visible;
                HomeSeedText.Text = game.HomeSeed.ToString();
                try
                {
                    var c = (Color)ColorConverter.ConvertFromString(game.HomeColor);
                    HomeSeedBorder.Background = new SolidColorBrush(Color.FromArgb(128, c.R, c.G, c.B));
                }
                catch { HomeSeedBorder.Background = new SolidColorBrush(Color.FromArgb(128, 51, 51, 51)); }
            }
            else
            {
                HomeSeedBorder.Visibility = Visibility.Collapsed;
            }

            // Highlight winning team
            if (game.State != GameState.Pre)
            {
                var winColor = new SolidColorBrush(Colors.White);
                var loseColor = new SolidColorBrush(Color.FromRgb(130, 130, 130));

                AwayScoreText.Foreground = game.AwayScore >= game.HomeScore ? winColor : loseColor;
                AwayTeamText.Foreground = game.AwayScore >= game.HomeScore ? winColor : loseColor;
                HomeScoreText.Foreground = game.HomeScore >= game.AwayScore ? winColor : loseColor;
                HomeTeamText.Foreground = game.HomeScore >= game.AwayScore ? winColor : loseColor;
            }
        });
    }

    private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        DragMove();
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
        Close();
    }
}
