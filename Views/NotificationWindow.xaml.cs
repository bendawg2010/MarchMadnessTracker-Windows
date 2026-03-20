using System.Windows;
using System.Windows.Threading;

namespace MarchMadnessTracker.Views;

public partial class NotificationWindow : Window
{
    private readonly DispatcherTimer _closeTimer;

    public NotificationWindow(string title, string message)
    {
        InitializeComponent();

        TitleText.Text = title;
        MessageText.Text = message;

        // Position in bottom-right corner of screen
        var workArea = SystemParameters.WorkArea;
        Left = workArea.Right - Width - 16;
        Top = workArea.Bottom - Height - 16;

        // Auto-close after 5 seconds
        _closeTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromSeconds(5)
        };
        _closeTimer.Tick += (s, e) =>
        {
            _closeTimer.Stop();
            Close();
        };
        _closeTimer.Start();
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
        _closeTimer.Stop();
        Close();
    }
}
