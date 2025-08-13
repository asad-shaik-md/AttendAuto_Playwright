# Jain University Attendance Checker - Playwright Version with Gemini AI

This is an enhanced Playwright-based version of the attendance checker script for Jain University with **automatic captcha solving using Google's Gemini AI**. It provides fully automated attendance checking without any manual intervention.

## 🚀 Features

- **🤖 AI-Powered Captcha Solving**: Automatic captcha solving using Google Gemini AI
- **🔐 Terminal-Based Authentication**: Secure credential input in terminal
- **⚡ Full Automation**: No manual intervention required after entering credentials
- **🌐 Multiple Browser Support**: Choose between Chromium, Firefox, or WebKit
- **📊 Detailed Reporting**: Subject-wise attendance breakdown and overall statistics
- **🛡️ Robust Error Handling**: Multiple fallback strategies and detailed error messages
- **💻 Cross-Platform**: Works on Windows, macOS, and Linux

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **Gemini API Key** (free from Google AI Studio)
3. **Active internet connection**

## 🛠️ Installation

### Quick Setup (Recommended)

1. **Run the Gemini setup script:**
   ```bash
   ./setup_gemini.sh
   ```
   
   Or manually:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

### Configure Default Credentials (Optional)

For convenience, you can store your credentials in config.py:

```bash
python setup_credentials.py
```

This will prompt for your student code and DOB password and store them securely in config.

### Get Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

You can either:
- Set it directly in `config.py`: `GEMINI_API_KEY = "your-key-here"`
- Set it as an environment variable: `export GEMINI_API_KEY='your-api-key-here'`
- Or enter it when prompted by the script

## 🎯 Usage

### Quick Start (with stored credentials)

```bash
python attendance_checker.py
```

If you've configured default credentials, the script will use them automatically.

### Basic Usage (manual entry)

```bash
python attendance_checker.py
```

The script will:
1. Prompt for your Gemini API key (if not set as environment variable)
2. Ask for your student credentials securely
3. Automatically solve captchas and login
4. Extract attendance data for all subjects
5. Display detailed attendance statistics

## ⚙️ Configuration

The script uses `config.py` for customization:

```python
# Browser settings
BROWSER_TYPE = "firefox"  # "chromium", "firefox", or "webkit"
HEADLESS = False  # Set to True for headless mode

# Gemini AI settings
GEMINI_API_KEY = "your-api-key-here"  # Or None to prompt
GEMINI_MODEL = "gemini-1.5-flash"  # AI model for captcha solving
CAPTCHA_PROMPT = "return only the text in the image and the text is always in capital"

# Default credentials (optional)
DEFAULT_STUDENT_CODE = None  # Set your student code or None to prompt
DEFAULT_DOB_PASSWORD = None  # Set your DOB (DDMMYYYY) or None to prompt

# Attendance thresholds
GOOD_ATTENDANCE_THRESHOLD = 75
WARNING_ATTENDANCE_THRESHOLD = 65
```

### Credential Management

**Setup default credentials:**
```bash
python setup_credentials.py  # Interactive setup
```

**Clear stored credentials:**
```bash
python clear_credentials.py  # Remove from config for security
```

## 🔒 Security Features

- **Secure credential input**: Passwords are hidden when typing
- **No credential storage**: Credentials are only kept in memory during execution
- **API key protection**: Gemini API key can be set as environment variable
- **Safe browser automation**: Uses secure browser contexts

## 🎛️ Advanced Usage

### Environment Variables

```bash
# Set Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Run the script
python attendance_checker.py
```

### Headless Mode

For running on servers or CI/CD:

```python
# In config.py
HEADLESS = True
```

### Different Browser

```python
# In config.py
BROWSER_TYPE = "chromium"  # or "webkit"
```

## 🐛 Troubleshooting

### Common Issues

1. **"Import google.generativeai could not be resolved"**
   - Run: `pip install google-generativeai`

2. **"Import PIL could not be resolved"**
   - Run: `pip install pillow`

3. **Captcha solving fails**
   - Check your Gemini API key
   - Ensure you have sufficient API quota
   - Try refreshing the captcha

4. **Login fails repeatedly**
   - Verify your credentials
   - Check if the website structure has changed
   - Update selectors in `config.py` if needed

5. **Browser doesn't start**
   - Run: `playwright install`
   - Try a different browser type in config

### Debug Mode

For detailed debugging, you can:
1. Set `HEADLESS = False` to see the browser
2. Add print statements in the code
3. Check the browser developer tools

## 📁 Project Structure

```
playwright-version-gemini/
├── attendance_checker.py    # Main script with Gemini AI integration
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── setup_gemini.sh        # Quick setup script
├── form.html              # Sample form structure (for reference)
├── README.md              # This file
└── activate_env.sh        # Virtual environment activation
```

## 🔄 Migration from Manual Version

If you're upgrading from the manual version:

1. **No more manual captcha solving** - Everything is automated
2. **Credentials in terminal** - No more browser-based input
3. **Faster execution** - AI solves captchas in seconds
4. **Better reliability** - Handles multiple login attempts

## 📈 Performance

- **Captcha solving**: ~2-5 seconds per captcha
- **Login process**: ~10-15 seconds total
- **Attendance extraction**: ~1-2 seconds per subject
- **Total runtime**: ~30-60 seconds (depending on number of subjects)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Disclaimer

This tool is for educational purposes only. Users are responsible for:
- Complying with their institution's terms of service
- Using their own credentials responsibly
- Respecting rate limits and fair usage

## 📄 License

This project is provided as-is for educational purposes. Use responsibly and in accordance with your institution's policies.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Gemini API key and quota
3. Ensure all dependencies are properly installed
4. Check if the website structure has changed

## 🎉 Acknowledgments

- **Playwright** team for the excellent automation framework
- **Google** for providing the Gemini AI API
- **Jain University** for their student portal (used responsibly)

---

**Happy automated attendance checking! 🎓**

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Activate on macOS/Linux:
   source venv/bin/activate
   
   # Activate on Windows:
   venv\Scripts\activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install
   ```
   
   Or install only specific browsers:
   ```bash
   playwright install chromium  # For Chromium only
   playwright install firefox   # For Firefox only
   playwright install webkit    # For WebKit only
   ```

## Usage

### If you used the automated setup with virtual environment:

1. **Quick run (easiest):**
   ```bash
   # On macOS/Linux:
   ./run_attendance_checker.sh
   
   # On Windows:
   run_attendance_checker.bat
   ```

2. **Or activate environment first:**
   ```bash
   # On macOS/Linux:
   source ./activate_env.sh
   python attendance_checker.py
   
   # On Windows:
   activate_env.bat
   python attendance_checker.py
   ```

### Manual execution:

1. **Run the script:**
   ```bash
   # If using virtual environment, activate it first:
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   
   # Then run:
   python attendance_checker.py
   ```

### Login Process:
2. **Manual login steps:**
   - The browser will open to the Jain University login page
   - Enter your College ID
   - Enter your Date of Birth
   - Solve the CAPTCHA
   - Click the Login button
   - Press Enter in the terminal when login is complete

3. **Automated data extraction:**
   - The script will navigate to the attendance page
   - Click expand icons for each subject
   - Extract conducted and attended counts
   - Calculate and display results

## Configuration

Modify `config.py` to customize the behavior:

### Browser Settings
```python
BROWSER_TYPE = "chromium"  # "chromium", "firefox", or "webkit"
HEADLESS = False           # Set to True for headless mode
VIEWPORT_SIZE = {"width": 1320, "height": 720}
```

### Timing Settings
```python
WAIT_TIMEOUT = 20000      # 20 seconds (in milliseconds)
INTERACTION_DELAY = 500   # 0.5 seconds (in milliseconds)
```

### Attendance Thresholds
```python
GOOD_ATTENDANCE_THRESHOLD = 75      # Green status
WARNING_ATTENDANCE_THRESHOLD = 65   # Yellow status
```

### Selectors
The script uses both CSS selectors and XPath for maximum compatibility:
```python
PLUS_ICON_SELECTOR = "i.bx-plus-circle"                    # CSS
PLUS_ICON_XPATH = "//i[contains(@class, 'bx-plus-circle')]"  # XPath
```

## Differences from Selenium Version

### Advantages of Playwright Version:

1. **Faster**: Playwright is generally faster than Selenium
2. **More Reliable**: Better element detection and waiting mechanisms
3. **Modern Syntax**: Uses async/await for cleaner code
4. **Multiple Browsers**: Easy switching between browser engines
5. **Better Network Control**: Can intercept and modify network requests
6. **Auto-waiting**: Automatically waits for elements to be ready

### Migration Notes:

- **Async Functions**: All browser operations are now async
- **Different API**: Uses Playwright's API instead of Selenium's WebDriver
- **Timeouts**: Specified in milliseconds instead of seconds
- **Selectors**: Supports both CSS selectors and XPath natively

## Troubleshooting

### Browser Installation Issues
If browsers don't install properly:
```bash
# Reinstall Playwright and browsers
pip uninstall playwright
pip install playwright
playwright install
```

### Permission Issues (macOS/Linux)
```bash
# Make sure Python has accessibility permissions
# Go to System Preferences > Security & Privacy > Privacy > Accessibility
# Add your terminal application
```

### Element Not Found
If selectors don't work:
1. Check the browser console for any changes in the website structure
2. Update selectors in `config.py`
3. Use browser developer tools to inspect elements

### Network Issues
```bash
# For corporate networks or proxy issues
export HTTPS_PROXY=your-proxy-url
export HTTP_PROXY=your-proxy-url
```

## Advanced Usage

### Headless Mode
For running without GUI (useful for servers):
```python
# In config.py
HEADLESS = True
```

### Custom Browser Arguments
```python
# In attendance_checker.py, modify the browser launch
self.browser = await self.playwright.chromium.launch(
    headless=config.HEADLESS,
    args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--your-custom-arg"
    ]
)
```

### Screenshots and Debugging
Add debugging features:
```python
# Take screenshot before extraction
await self.page.screenshot(path="debug.png")

# Print page content for debugging
content = await self.page.content()
print(content[:1000])  # First 1000 characters
```

## Requirements

- Python 3.7+
- Playwright
- Internet connection
- Valid Jain University student credentials

## Support

If you encounter issues:
1. Check that your credentials are correct
2. Verify the university website is accessible
3. Update selectors if the website structure has changed
4. Check browser compatibility

## License

This script is for educational purposes. Please use responsibly and in accordance with your university's terms of service.
