#!/bin/bash

# Attendance Checker - macOS/Linux Startup Script
# This script will set up and run the attendance checker application

echo ""
echo "===================================="
echo " Attendance Checker Startup Script"
echo "===================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    if ! command_exists python; then
        echo "ERROR: Python is not installed"
        echo "Please install Python 3.8 or higher"
        echo "macOS: brew install python3"
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
        read -p "Press Enter to exit..."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python found. Checking version..."
$PYTHON_CMD --version

# Check if pip is available
if ! command_exists pip3 && ! command_exists pip; then
    echo "ERROR: pip is not available"
    echo "Please install pip"
    read -p "Press Enter to exit..."
    exit 1
fi

# Determine pip command
if command_exists pip3; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

echo "Installing/updating Python dependencies..."
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "Installing Playwright browsers..."
$PYTHON_CMD -m playwright install

if [ $? -ne 0 ]; then
    echo "WARNING: Playwright browser installation failed"
    echo "The application may still work if browsers are already installed"
fi

echo ""
echo "Starting the Attendance Checker application..."
echo "The application will find an available port automatically (5001, 5002, 5003, etc.)"
echo ""

# Start the application in background and capture output
$PYTHON_CMD webapp.py > app_output.log 2>&1 &
APP_PID=$!

# Wait a moment for the server to start
sleep 5

# Try to extract the port from the output
if [ -f app_output.log ]; then
    PORT=$(grep "Access the web interface at:" app_output.log | sed -n 's/.*localhost:\([0-9]*\).*/\1/p')
    cat app_output.log
fi

# If we couldn't extract the port, try common ports
if [ -z "$PORT" ]; then
    echo "Could not determine exact port, trying common ports..."
    PORT="5001"
fi

# Open the browser
APP_URL="http://localhost:$PORT"
echo ""
echo "Application started successfully!"
echo "Application PID: $APP_PID"
echo "Access URL: $APP_URL"
echo ""

if command_exists open; then
    # macOS
    open "$APP_URL"
elif command_exists xdg-open; then
    # Linux
    xdg-open "$APP_URL"
elif command_exists firefox; then
    firefox "$APP_URL" &
elif command_exists google-chrome; then
    google-chrome "$APP_URL" &
elif command_exists chromium-browser; then
    chromium-browser "$APP_URL" &
else
    echo "Could not automatically open browser."
    echo "Please manually open: $APP_URL"
fi

# Wait for the Python process to finish
wait $APP_PID
