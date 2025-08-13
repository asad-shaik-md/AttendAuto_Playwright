@echo off
REM Attendance Checker - Windows Startup Script
REM This script will set up and run the attendance checker application

echo.
echo ====================================
echo  Attendance Checker Startup Script
echo ====================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking dependencies...

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo Installing/updating Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installing Playwright browsers...
playwright install

if errorlevel 1 (
    echo WARNING: Playwright browser installation failed
    echo The application may still work if browsers are already installed
)

echo.
echo Starting the Attendance Checker application...
echo The application will find an available port automatically (5001, 5002, 5003, etc.)
echo.

REM Start the application in background and open browser
start /b python webapp.py

REM Wait a moment for the server to start
timeout /t 5 /nobreak >nul

REM Try opening common ports - one of them should work
start http://localhost:5001 2>nul
timeout /t 1 /nobreak >nul
start http://localhost:5002 2>nul
timeout /t 1 /nobreak >nul
start http://localhost:5003 2>nul

echo.
echo Application started! Check the console output above for the exact URL.
echo If browser didn't open automatically, check the application output for the correct port.

echo.
echo Application started successfully!
echo Close this window to stop the application.
echo.

REM Keep the window open
pause
