using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using MarchMadnessTracker.ViewModels;

namespace MarchMadnessTracker;

public partial class MainWindow : Window
{
    public MainWindow(IServiceProvider serviceProvider)
    {
        InitializeComponent();
        DataContext = serviceProvider.GetRequiredService<MainViewModel>();
    }

    protected override void OnClosed(EventArgs e)
    {
        base.OnClosed(e);
        // Don't quit the app, just hide - app lives in tray
    }
}
