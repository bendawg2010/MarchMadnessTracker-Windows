using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using MarchMadnessTracker.Models;
using MarchMadnessTracker.ViewModels;

namespace MarchMadnessTracker.Views;

public partial class ScoresView : UserControl
{
    public ScoresView()
    {
        InitializeComponent();
    }

    private void GameCard_Click(object sender, MouseButtonEventArgs e)
    {
        if (sender is FrameworkElement element && element.DataContext is GameData game)
        {
            if (DataContext is ScoresViewModel vm)
            {
                vm.DetachGameCommand.Execute(game);
            }
        }
    }
}
