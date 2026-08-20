@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo   YouTube Competitor Tracker
echo ========================================
echo.
echo Starting app... If it closes, check the error below:
echo.

python -m app.main 2>&1

echo.
echo ========================================
echo   App exited with error above
echo ========================================
echo.
echo Press any key to close...
pause >nul
