"""
Jain University Attendance Checker Configuration (Playwright Version)
====================================================================

This file contains all the configuration settings for the attendance checker.
Environment variables are loaded from .env file for sensitive data.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# URLs
LOGIN_URL = "https://student.jgianveshana.com"
ATTENDANCE_URL = "https://student.jgianveshana.com/ui/Academics/js_Class_Attendance_for_a_Week.aspx"

# Login success/failure URL indicators
LOGIN_SUCCESS_URL = "https://student.jgianveshana.com/ui/dashboard/index.aspx"
LOGIN_FAILURE_URL = "https://student.jgianveshana.com/"

# Timeouts and delays (in milliseconds for Playwright)
WAIT_TIMEOUT = 15000  # 15 seconds (reduced from 20)
INTERACTION_DELAY = 200  # 0.2 seconds (reduced from 0.5)

# Browser settings
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "firefox")  # Can be "chromium", "firefox", or "webkit"
HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"  # Set to True for headless mode
VIEWPORT_SIZE = {"width": 1320, "height": 720}

# Attendance thresholds (percentages)
GOOD_ATTENDANCE_THRESHOLD = 75
WARNING_ATTENDANCE_THRESHOLD = 65

# CSS/XPath selectors for web elements
PLUS_ICON_SELECTOR = "i.bx-plus-circle"  # CSS selector
PLUS_ICON_XPATH = "//i[contains(@class, 'bx-plus-circle')]"
CONDUCTED_TEXT_SELECTOR = "span[id*='lblClsCondID']"  # CSS selector
CONDUCTED_TEXT_XPATH = "//span[contains(@id, 'lblClsCondID')]"
TOTAL_TEXT_SELECTOR = "span[id*='lblClsAttID']"  # CSS selector
TOTAL_TEXT_XPATH = "//span[contains(@id, 'lblClsAttID')]"

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Will be loaded from .env file or prompted during runtime
GEMINI_MODEL = "gemini-2.5-flash"  # Model to use for captcha solving

# Multiple prompts to try for better results
CAPTCHA_PROMPTS = [
    "Extract only the alphanumeric text from this captcha image. Return just the characters with no explanations, no prefixes, no quotes - only the pure text characters.",
    "What text is shown in this captcha image? Reply with only the text characters in.",
    "Read the captcha code from this image. Output only the code.",
    "OCR this captcha image. Return only the alphanumeric characters."
]

# Fallback to the first prompt for compatibility
CAPTCHA_PROMPT = CAPTCHA_PROMPTS[0]

# Default Student Credentials (loaded from .env file or will prompt if not set)
DEFAULT_STUDENT_CODE = os.getenv("STUDENT_CODE")  # Set in .env file or leave None to prompt
DEFAULT_DOB_PASSWORD = os.getenv("DOB_PASSWORD")  # Set in .env file or leave None to prompt

# Login form selectors
USERNAME_FIELD = "input[name='txtUserName']"
PASSWORD_FIELD = "input[name='txtPassword']"
CAPTCHA_FIELD = "input[name='txtCaptcha']"
CAPTCHA_IMAGE = "img[src*='CaptchaImage.axd']"
LOGIN_BUTTON = "input[name='btnLogIn']"
REFRESH_CAPTCHA_BUTTON = "a[id='lnkbtnrefresh']"
