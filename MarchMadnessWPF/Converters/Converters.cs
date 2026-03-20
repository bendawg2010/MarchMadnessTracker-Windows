using System.Globalization;
using System.Windows;
using System.Windows.Data;
using System.Windows.Media;
using MarchMadnessTracker.Models;

namespace MarchMadnessTracker.Converters;

public class BoolToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        bool invert = parameter?.ToString() == "Invert";
        bool val = value is bool b && b;
        if (invert) val = !val;
        return val ? Visibility.Visible : Visibility.Collapsed;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class CollectionCountToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is int count)
            return count > 0 ? Visibility.Visible : Visibility.Collapsed;
        if (value is System.Collections.ICollection col)
            return col.Count > 0 ? Visibility.Visible : Visibility.Collapsed;
        return Visibility.Collapsed;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class GameStateToColorConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is GameState state)
        {
            return state switch
            {
                GameState.In => new SolidColorBrush(Color.FromRgb(76, 175, 80)),   // Green
                GameState.Post => new SolidColorBrush(Color.FromRgb(158, 158, 158)), // Gray
                _ => new SolidColorBrush(Color.FromRgb(100, 181, 246))              // Blue
            };
        }
        return new SolidColorBrush(Colors.White);
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class GameStateToBadgeConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is GameState state)
        {
            return state switch
            {
                GameState.In => "LIVE",
                GameState.Post => "FINAL",
                _ => "UPCOMING"
            };
        }
        return "";
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class UpsetToBorderConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is bool isUpset && isUpset)
            return new SolidColorBrush(Color.FromRgb(255, 152, 0)); // Orange
        return new SolidColorBrush(Color.FromRgb(66, 66, 66));
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class SeedToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is int seed)
            return seed > 0 ? Visibility.Visible : Visibility.Collapsed;
        return Visibility.Collapsed;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class HexToColorConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is string hex && !string.IsNullOrEmpty(hex))
        {
            try
            {
                var color = (Color)ColorConverter.ConvertFromString(hex);
                return new SolidColorBrush(Color.FromArgb(80, color.R, color.G, color.B));
            }
            catch { }
        }
        return new SolidColorBrush(Color.FromArgb(80, 51, 51, 51));
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class ScoreHighlightConverter : IMultiValueConverter
{
    public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
    {
        if (values.Length >= 3 &&
            values[0] is int score1 &&
            values[1] is int score2 &&
            values[2] is GameState state &&
            state != GameState.Pre)
        {
            string side = parameter?.ToString() ?? "home";
            bool isWinning = side == "home" ? score1 > score2 : score2 > score1;
            return isWinning
                ? new SolidColorBrush(Colors.White)
                : new SolidColorBrush(Color.FromRgb(158, 158, 158));
        }
        return new SolidColorBrush(Colors.White);
    }

    public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}
