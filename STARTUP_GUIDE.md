# Quick Start Guide

This project includes convenient startup scripts for different operating systems:

## Windows (.bat file)
- **File**: `start_app.bat`
- **Usage**: Double-click the file in Windows Explorer
- **What it does**:
  - Checks for Python installation
  - Installs required dependencies
  - Installs Playwright browsers
  - Starts the web application
  - Opens your default browser to http://localhost:5001

## macOS/Linux (.command file)
- **File**: `start_app.command`
- **Usage**: Double-click the file in Finder (macOS) or run in terminal
- **What it does**:
  - Checks for Python installation
  - Installs required dependencies
  - Installs Playwright browsers
  - Starts the web application
  - Opens your default browser to http://localhost:5001

## Prerequisites
- Python 3.8 or higher
- Internet connection (for installing dependencies)

## Manual Installation (if scripts fail)
If the automatic scripts don't work, you can run these commands manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Start the application
python webapp.py
```

Then open your browser to: http://localhost:5001

## Troubleshooting
- If Python is not found, make sure it's installed and added to your system PATH
- If pip is not found, ensure it was installed with Python
- If you get permission errors on macOS/Linux, the script should already be executable, but you can run: `chmod +x start_app.command`
- If the browser doesn't open automatically, manually navigate to http://localhost:5001

## Stopping the Application
- **Windows**: Close the command prompt window or press Ctrl+C
- **macOS/Linux**: Press Ctrl+C in the terminal or close the terminal window
