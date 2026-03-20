@echo off
REM ── Build March Madness Tracker as standalone Windows .exe ──
REM Requires: pip install -r requirements.txt

echo.
echo ====================================
echo  March Madness Tracker - Build
echo ====================================
echo.

REM Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/3] Building executable with PyInstaller...
pyinstaller --noconfirm --onefile --windowed ^
    --name "MarchMadnessTracker" ^
    --icon=NONE ^
    --add-data "ui;ui" ^
    --hidden-import=pystray._win32 ^
    --hidden-import=plyer.platforms.win.notification ^
    main.py

if %ERRORLEVEL% neq 0 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Build complete!
echo.
echo Executable: dist\MarchMadnessTracker.exe
echo.
pause
