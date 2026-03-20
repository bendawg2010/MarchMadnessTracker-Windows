using System.Windows;

namespace MarchMadnessTracker.Services;

public class NotificationService
{
    public void ShowNotification(string title, string message)
    {
        // Use WPF's built-in mechanism via the tray icon
        Application.Current?.Dispatcher.Invoke(() =>
        {
            try
            {
                // Show a toast-style notification window
                var notification = new Views.NotificationWindow(title, message);
                notification.Show();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Notification error: {ex.Message}");
            }
        });
    }
}
