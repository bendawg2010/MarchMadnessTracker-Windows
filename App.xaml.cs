using System.Drawing;
using System.IO;
using System.Windows;
using Hardcodet.NotifyIcon.Wpf;
using Microsoft.Extensions.DependencyInjection;
using MarchMadnessTracker.Services;
using MarchMadnessTracker.ViewModels;

namespace MarchMadnessTracker;

public partial class App : Application
{
    private TaskbarIcon? _trayIcon;
    private IServiceProvider _serviceProvider = null!;

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        var services = new ServiceCollection();
        ConfigureServices(services);
        _serviceProvider = services.BuildServiceProvider();

        // Create tray icon programmatically
        _trayIcon = new TaskbarIcon
        {
            ToolTipText = "March Madness Tracker - Click to open",
            Icon = CreateBasketballIcon()
        };

        // Context menu
        var contextMenu = new System.Windows.Controls.ContextMenu();

        var openItem = new System.Windows.Controls.MenuItem { Header = "Open Tracker" };
        openItem.Click += (s, args) => ShowMainWindow();

        var quitItem = new System.Windows.Controls.MenuItem { Header = "Quit" };
        quitItem.Click += (s, args) => QuitApplication();

        contextMenu.Items.Add(openItem);
        contextMenu.Items.Add(new System.Windows.Controls.Separator());
        contextMenu.Items.Add(quitItem);

        _trayIcon.ContextMenu = contextMenu;
        _trayIcon.TrayMouseDoubleClick += (s, args) => ShowMainWindow();
        _trayIcon.TrayLeftMouseUp += (s, args) => ShowMainWindow();

        // Start polling
        var poller = _serviceProvider.GetRequiredService<ScorePoller>();
        poller.Start();

        // Show main window on first launch
        ShowMainWindow();
    }

    private void ConfigureServices(IServiceCollection services)
    {
        services.AddSingleton<SettingsService>();
        services.AddSingleton<EspnService>();
        services.AddSingleton<ScorePoller>();
        services.AddSingleton<NotificationService>();
        services.AddSingleton<MainViewModel>();
        services.AddSingleton<ScoresViewModel>();
        services.AddSingleton<BracketViewModel>();
        services.AddSingleton<ScheduleViewModel>();
        services.AddSingleton<SettingsViewModel>();
    }

    private static System.Drawing.Icon CreateBasketballIcon()
    {
        // Create a simple basketball-style icon programmatically
        using var bitmap = new Bitmap(32, 32);
        using var g = Graphics.FromImage(bitmap);

        g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

        // Orange circle (basketball)
        using var orangeBrush = new SolidBrush(System.Drawing.Color.FromArgb(255, 152, 0));
        g.FillEllipse(orangeBrush, 2, 2, 28, 28);

        // Dark lines on ball
        using var linePen = new Pen(System.Drawing.Color.FromArgb(120, 80, 0), 1.5f);
        g.DrawEllipse(linePen, 2, 2, 28, 28);
        g.DrawLine(linePen, 16, 2, 16, 30);     // vertical line
        g.DrawLine(linePen, 2, 16, 30, 16);     // horizontal line
        g.DrawArc(linePen, 6, 2, 20, 28, 0, 180);  // curved line

        // Convert bitmap to icon
        var hIcon = bitmap.GetHicon();
        return System.Drawing.Icon.FromHandle(hIcon);
    }

    public void ShowMainWindow()
    {
        var mainWindow = Windows.OfType<MainWindow>().FirstOrDefault();
        if (mainWindow == null)
        {
            mainWindow = new MainWindow(_serviceProvider);
            mainWindow.Show();
        }
        else
        {
            mainWindow.Activate();
        }
    }

    public void QuitApplication()
    {
        var poller = _serviceProvider.GetService<ScorePoller>();
        poller?.Stop();

        _trayIcon?.Dispose();
        Current.Shutdown();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _trayIcon?.Dispose();
        base.OnExit(e);
    }

    public IServiceProvider Services => _serviceProvider;
}
