#!/usr/bin/env python3
"""
Jain University Attendance Checker (Playwright Version with Gemini AI)
======================================================================

This script automates the process of checking attendance on the Jain University student portal.
It uses Gemini AI to solve captchas automatically and prompts for credentials in the terminal.
This version uses Playwright for better performance and reliability.

Features:
- Automated captcha solving using Gemini AI
- Terminal-based credential input
- Full automation (no manual intervention required)

Author: Automated Attendance Checker
Date: August 2025
"""

import asyncio
import time
import re
import os
import sys
import getpass
import base64
from io import BytesIO
from playwright.async_api import async_playwright
import google.generativeai as genai
from PIL import Image
import requests
import config


class JainAttendanceChecker:
    """
    A class to handle Jain University attendance checking automation using Playwright and Gemini AI.
    """
    
    def __init__(self, username=None, password=None):
        self.browser = None
        self.page = None
        self.context = None
        self.conducted_list = []
        self.attended_list = []
        self.subject_names = []  # Store actual subject names
        self.username = username
        self.password = password
        self.gemini_model = None
        self.logger = None  # Can be set by webapp for WebSocket logging
    
    def log(self, message, level='info'):
        """Log message - can be overridden by webapp"""
        print(message)
        if hasattr(self, 'logger') and self.logger:
            self.logger.log(message, level)
    
    def setup_gemini(self):
        """
        Initialize Gemini AI for captcha solving.
        """
        print("Setting up Gemini AI for captcha solving...")
        
        # Get API key from environment variable or config or prompt user
        api_key = os.getenv('GEMINI_API_KEY') or config.GEMINI_API_KEY
        
        if api_key:
            print("Using configured/environment Gemini API key")
        else:
            print("\nGemini API Key is required for captcha solving.")
            print("You can get a free API key from: https://aistudio.google.com/app/apikey")
            api_key = getpass.getpass("Enter your Gemini API Key: ").strip()
            
            if not api_key:
                print("✗ API key is required. Exiting...")
                sys.exit(1)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel(config.GEMINI_MODEL)
        print("✓ Gemini AI setup complete")
    
    def get_credentials(self):
        """
        Get user credentials from config or prompt in terminal.
        """
        print("\n" + "="*50)
        print("LOGIN CREDENTIALS")
        print("="*50)
        
        # Get student code from config or prompt
        if config.DEFAULT_STUDENT_CODE:
            self.username = config.DEFAULT_STUDENT_CODE
            print(f"Using configured student code: {self.username}")
        else:
            self.username = input("Enter your Student Code: ").strip()
            if not self.username:
                print("✗ Username is required. Exiting...")
                sys.exit(1)
        
        # Get DOB password from config or prompt
        if config.DEFAULT_DOB_PASSWORD:
            self.password = config.DEFAULT_DOB_PASSWORD
            print("Using configured DOB password: [hidden]")
        else:
            self.password = getpass.getpass("Enter your Password (DDMMYYYY): ").strip()
            if not self.password:
                print("✗ Password is required. Exiting...")
                sys.exit(1)
        
        print("✓ Credentials obtained")
    
    def clean_captcha_character(self, char: str) -> str:
        """
        Clean individual captcha character to ensure it's properly formatted
        """
        if not char:
            return ""
        
        # Convert to string and strip whitespace
        char = str(char).strip()
        
        # Remove any Unicode control characters
        import unicodedata
        char = ''.join(c for c in char if unicodedata.category(c) != 'Cc')
        
        # Convert to uppercase
        char = char.upper()
        
        # Only keep alphanumeric characters
        if char.isalnum():
            return char
        
        return ""

    def clean_captcha_response(self, text: str) -> str:
        """
        Enhanced text cleaning for captcha responses.
        
        Args:
            text (str): Raw response from Gemini AI
            
        Returns:
            str: Cleaned captcha text or None if invalid
        """
        if not text:
            return None
            
        print(f"    🧹 Cleaning raw response: '{text}'")
        print(f"    🧹 Raw bytes: {text.encode('utf-8')}")
        
        # Enhanced text cleaning process
        captcha_text = text
        
        # Step 1: Strip whitespace and convert to uppercase
        captcha_text = captcha_text.strip().upper()
        
        # Step 2: Remove common unwanted prefixes/suffixes that AI might add
        unwanted_patterns = [
            'THE TEXT IS:', 'TEXT:', 'CAPTCHA:', 'ANSWER:', 'RESULT:', 
            'THE ANSWER IS:', 'THE CAPTCHA IS:', 'THE CODE IS:',
            'CODE:', 'IMAGE CONTAINS:', 'I SEE:', 'THE IMAGE SHOWS:',
            'THE TEXT IN THE IMAGE IS:', 'CAPTCHA TEXT:', 'THE CAPTCHA TEXT IS:'
        ]
        for pattern in unwanted_patterns:
            if captcha_text.startswith(pattern):
                captcha_text = captcha_text[len(pattern):].strip()
                break
        
        # Step 3: Extract alphanumeric sequences (in case there's explanation text)
        import re
        # Find sequences of 3-8 alphanumeric characters (typical captcha length)
        matches = re.findall(r'[A-Z0-9]{3,8}', captcha_text)
        if matches:
            # Use the first reasonable match
            captcha_text = matches[0]
            print(f"    🎯 Extracted sequence: '{captcha_text}'")
        
        # Step 4: Remove quotes and common punctuation that might be added
        captcha_text = captcha_text.strip('\'".,!?-_()[]{}:;')
        
        # Step 5: Normalize Unicode characters and remove invisible characters
        import unicodedata
        captcha_text = unicodedata.normalize('NFKD', captcha_text)
        
        # Step 6: Remove any remaining non-alphanumeric characters
        captcha_text = re.sub(r'[^A-Z0-9]', '', captcha_text)
        
        # Step 7: Final validation and length check
        if captcha_text and len(captcha_text) >= 3 and len(captcha_text) <= 10:
            print(f"    ✅ Cleaned captcha: '{captcha_text}' (length: {len(captcha_text)})")
            print(f"    ✅ Final bytes: {captcha_text.encode('utf-8')}")
            return captcha_text
        elif captcha_text and len(captcha_text) > 10:
            # If it's too long, try to extract the most likely captcha part
            # Look for patterns at the end or beginning
            possible_codes = re.findall(r'[A-Z0-9]{4,6}', captcha_text)
            if possible_codes:
                best_match = possible_codes[0]  # Take the first reasonable match
                print(f"    🔍 Extracted from long text: '{best_match}'")
                return best_match
            else:
                print(f"    ⚠️ Text too long, taking first 6 chars: '{captcha_text[:6]}'")
                return captcha_text[:6] if len(captcha_text) >= 3 else None
        else:
            print(f"    ⚠️ Suspicious captcha length ({len(captcha_text) if captcha_text else 0}): '{captcha_text}'")
            return captcha_text if captcha_text else None
    
    async def solve_captcha_with_gemini(self, captcha_image_url: str, max_retries: int = 3) -> str:
        """
        Solve captcha using Gemini AI with multiple prompt strategies
        Downloads the image from URL and processes it with enhanced text cleaning
        """
        import google.generativeai as genai
        from PIL import Image
        import time
        import re
        import unicodedata
        import requests
        from io import BytesIO
        
        print(f"🤖 Initializing Gemini AI for captcha solving...")
        
        try:
            # Configure Gemini
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            # Download the captcha image
            print(f"📥 Downloading captcha from: {captcha_image_url}")
            response = requests.get(captcha_image_url)
            if response.status_code != 200:
                print(f"❌ Failed to download captcha image: {response.status_code}")
                return ""
            
            # Convert to PIL Image
            img = Image.open(BytesIO(response.content))
            print(f"📸 Loaded captcha image: {img.size}")
                
            # Try different prompts
            for attempt in range(max_retries):
                try:
                    # Use different prompts from our list
                    prompt_index = attempt % len(config.CAPTCHA_PROMPTS)
                    current_prompt = config.CAPTCHA_PROMPTS[prompt_index]
                    
                    print(f"🎯 Attempt {attempt + 1}/{max_retries} using prompt {prompt_index + 1}")
                    print(f"💭 Prompt: {current_prompt[:50]}...")
                    
                    # Generate response
                    ai_response = model.generate_content([current_prompt, img])
                    
                    if ai_response and ai_response.text:
                        raw_text = ai_response.text.strip()
                        print(f"🤖 Raw AI response: '{raw_text}'")
                        
                        # Clean the response
                        cleaned_text = self.clean_captcha_response(raw_text)
                        print(f"✨ Cleaned response: '{cleaned_text}'")
                        
                        # Validate the cleaned text
                        if cleaned_text and len(cleaned_text) >= 4 and cleaned_text.isalnum():
                            print(f"✅ Successfully solved captcha: {cleaned_text}")
                            return cleaned_text
                        else:
                            print(f"❌ Invalid captcha format, trying next prompt...")
                            continue
                    
                except Exception as e:
                        print(f"❌ Error with prompt {prompt_index + 1}: {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(1)
                            continue
                        
                # Small delay between attempts
                if attempt < max_retries - 1:
                    time.sleep(2)
            
            print(f"❌ All {max_retries} attempts failed")
            return ""
                
        except Exception as e:
            print(f"❌ Fatal error in Gemini AI: {str(e)}")
            return ""
    
    async def solve_captcha_with_screenshot(self, captcha_element):
        """
        Alternative method to solve captcha by taking a screenshot of the element.
        
        Args:
            captcha_element: Playwright element containing the captcha image
        
        Returns:
            str: Solved captcha text or None if failed
        """
        try:
            print("    📸 Taking screenshot of captcha element...")
            
            # Take screenshot of the captcha element
            screenshot_bytes = await captcha_element.screenshot()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(screenshot_bytes))
            print(f"    ✓ Screenshot captured: {image.size} pixels")
            
            # Generate content with Gemini
            print("    📤 Sending screenshot to Gemini AI...")
            ai_response = self.gemini_model.generate_content([
                config.CAPTCHA_PROMPT,
                image
            ])
            
            if ai_response.text:
                # Use the enhanced text cleaning process
                captcha_text = self.clean_captcha_response(ai_response.text)
                
                if captcha_text:
                    print(f"    ✓ Captcha solved (screenshot method): '{captcha_text}'")
                    return captcha_text
                else:
                    print(f"    ✗ No valid captcha text extracted from screenshot response")
                    return None
            else:
                print("    ✗ Gemini returned empty response")
                return None
                
        except Exception as e:
            print(f"    ✗ Error solving captcha with screenshot: {str(e)}")
            return None
    
    async def setup_browser(self):
        """
        Initialize browser with appropriate settings.
        """
        print("Setting up browser with Playwright...")
        
        self.playwright = await async_playwright().start()
        
        # Choose browser type based on config
        if config.BROWSER_TYPE == "firefox":
            self.browser = await self.playwright.firefox.launch(
                headless=config.HEADLESS,
                slow_mo=50
            )
        elif config.BROWSER_TYPE == "webkit":
            self.browser = await self.playwright.webkit.launch(
                headless=config.HEADLESS,
                slow_mo=50
            )
        else:  # Default to chromium
            self.browser = await self.playwright.chromium.launch(
                headless=config.HEADLESS,
                slow_mo=50,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-background-networking",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-gpu",
                    "--allow-running-insecure-content"
                ]
            )
        
        # Create a new browser context
        self.context = await self.browser.new_context(
            viewport=config.VIEWPORT_SIZE,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Create a new page
        self.page = await self.context.new_page()
        
        # Set default timeout
        self.page.set_default_timeout(config.WAIT_TIMEOUT)
        
        print("✓ Browser setup complete")
    
    async def automated_login(self):
        """
        Perform automated login with captcha solving and specific URL-based success detection.
        Will try exactly 2 times: if first attempt fails, retry once more.
        Success URL: https://student.jgianveshana.com/ui/dashboard/index.aspx
        Failure URL: https://student.jgianveshana.com/
        """
        print("\nPerforming automated login...")
        
        # Navigate to login page
        await self.page.goto(config.LOGIN_URL)
        print("✓ Navigated to login page")
        
        # Wait for page to load
        await self.page.wait_for_load_state("networkidle")
        
        max_attempts = 2  # Exactly 2 attempts as requested
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"\nLogin attempt {attempt}/{max_attempts}")
                
                # Fill username
                await self.page.fill(config.USERNAME_FIELD, self.username)
                print("  ✓ Username filled")
                
                # Fill password
                await self.page.fill(config.PASSWORD_FIELD, self.password)
                print("  ✓ Password filled")
                
                # Get captcha image URL
                captcha_img = await self.page.query_selector(config.CAPTCHA_IMAGE)
                if not captcha_img:
                    print("  ✗ Captcha image not found")
                    continue
                
                captcha_src = await captcha_img.get_attribute("src")
                print(f"  Raw captcha src: {captcha_src}")
                
                # Make the URL absolute - handle different URL formats
                if captcha_src.startswith("http"):
                    # Already absolute URL
                    captcha_url = captcha_src
                elif captcha_src.startswith("/"):
                    # Relative URL starting with /
                    captcha_url = f"https://student.jgianveshana.com{captcha_src}"
                else:
                    # Relative URL not starting with /
                    captcha_url = f"https://student.jgianveshana.com/{captcha_src}"
                
                print(f"  Final captcha URL: {captcha_url}")
                
                # Try to solve captcha with URL download first
                captcha_text = await self.solve_captcha_with_gemini(captcha_url)
                
                # If URL method failed, try screenshot method as fallback
                if not captcha_text:
                    print("  🔄 Trying screenshot method as fallback...")
                    captcha_text = await self.solve_captcha_with_screenshot(captcha_img)
                
                if not captcha_text:
                    print("  ✗ Failed to solve captcha with both methods")
                    if attempt < max_attempts:
                        # Refresh captcha and try again
                        refresh_btn = await self.page.query_selector(config.REFRESH_CAPTCHA_BUTTON)
                        if refresh_btn:
                            await refresh_btn.click()
                            await self.page.wait_for_timeout(2000)
                    continue
                
                # Fill captcha character by character
                await self.fill_captcha_character_by_character(captcha_text)
                
                # Click login button
                await self.page.click(config.LOGIN_BUTTON)
                print("  ✓ Login button clicked")
                
                # Wait for response and check URL
                await self.page.wait_for_timeout(5000)
                
                current_url = self.page.url
                print(f"  📍 Current URL after login: {current_url}")
                
                # Check for specific success or failure URLs
                if current_url == config.LOGIN_SUCCESS_URL:
                    print("  ✅ Login successful! (Dashboard URL detected)")
                    await self.page.wait_for_timeout(2000)  # Let session establish
                    return True
                elif current_url == config.LOGIN_FAILURE_URL:
                    print("  ❌ Login failed! (Still on login page)")
                    
                    # Check for specific error messages
                    error_element = await self.page.query_selector("#lblValid")
                    if error_element:
                        error_text = await error_element.text_content()
                        if error_text and error_text.strip():
                            print(f"  📝 Error message: {error_text.strip()}")
                    
                    if attempt < max_attempts:
                        print("  🔄 Retrying login attempt...")
                        # Refresh captcha for retry
                        refresh_btn = await self.page.query_selector(config.REFRESH_CAPTCHA_BUTTON)
                        if refresh_btn:
                            await refresh_btn.click()
                            await self.page.wait_for_timeout(2000)
                    continue
                else:
                    print(f"  ⚠️ Unexpected URL: {current_url}")
                    # For any other URL, treat as failure and retry if possible
                    if attempt < max_attempts:
                        print("  🔄 Unexpected response, retrying...")
                        continue
                    else:
                        print("  ❌ Login failed - unexpected URL after all attempts")
                        return False
                
            except Exception as e:
                print(f"  ❌ Error during login attempt {attempt}: {str(e)}")
                if attempt < max_attempts:
                    print("  🔄 Retrying due to error...")
                    continue
        
        print(f"❌ All {max_attempts} login attempts failed")
        return False
    
    async def navigate_to_attendance_page(self):
        """
        Navigate to the Class Attendance page after login.
        """
        print("\nNavigating to Class Attendance page...")
        
        # Check current URL before navigation
        current_url = self.page.url
        print(f"📍 Current URL before navigation: {current_url}")
        
        # Check if we have any session cookies
        cookies = await self.page.context.cookies()
        print(f"🍪 Current cookies count: {len(cookies)}")
        
        try:
            await self.page.goto(config.ATTENDANCE_URL)
            
            # Wait for page to load
            await self.page.wait_for_load_state("networkidle")
            
            # Check final URL
            final_url = self.page.url
            print(f"📍 Final URL after navigation: {final_url}")
            
            if "login" in final_url.lower():
                print("❌ Redirected back to login - session may have expired")
                
                # Check if there are any error messages or specific reasons
                error_msg = await self.page.query_selector(".error, .alert, .message")
                if error_msg:
                    error_text = await error_msg.text_content()
                    print(f"❌ Error message: {error_text}")
                
                return False
                
            print("✓ Attendance page loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Navigation error: {str(e)}")
            final_url = self.page.url
            print(f"📍 URL after error: {final_url}")
            return False
    
    async def fill_captcha_character_by_character(self, captcha_text: str):
        """
        Fill captcha field character by character to avoid formatting issues
        """
        print(f"  🔤 Filling captcha character by character: '{captcha_text}'")
        
        # Clear the field first
        await self.page.fill(config.CAPTCHA_FIELD, "")
        await self.page.wait_for_timeout(100)
        
        # Focus on the captcha field
        await self.page.focus(config.CAPTCHA_FIELD)
        await self.page.wait_for_timeout(100)
        
        # Type each character individually
        for i, char in enumerate(captcha_text):
            cleaned_char = self.clean_captcha_character(char)
            if cleaned_char:
                print(f"    Typing character {i+1}: '{cleaned_char}'")
                await self.page.keyboard.type(cleaned_char)
                await self.page.wait_for_timeout(150)  # Small delay between characters
            else:
                print(f"    Skipping invalid character at position {i+1}: '{char}'")
        
        # Verify what was actually typed
        field_value = await self.page.input_value(config.CAPTCHA_FIELD)
        print(f"  ✅ Field contains: '{field_value}'")
        
        return field_value
    
    async def extract_attendance_data(self):
        """
        Extract attendance data for all subjects by clicking expand icons.
        Finds plus icons, clicks them, and extracts conducted/attended numbers.
        """
        print("\nExtracting attendance data...")
        print(f"Looking for plus icons with selector: {config.PLUS_ICON_SELECTOR}")
        
        # Reset lists for fresh data
        self.conducted_list = []
        self.attended_list = []
        self.subject_names = []
        
        try:
            # Wait for page to fully load first
            await self.page.wait_for_load_state("domcontentloaded")
            await self.page.wait_for_timeout(2000)  # Give extra time for dynamic content
            
            # Debug: Check what's on the page
            print("Current page URL:", self.page.url)
            print("Page title:", await self.page.title())
            
            # First, extract all subject names before clicking anything
            await self.extract_all_subject_names()
            
            # Try to find plus icons with multiple strategies
            plus_icons = []
            
            # Strategy 1: CSS selector
            try:
                plus_icons = await self.page.query_selector_all(config.PLUS_ICON_SELECTOR)
                print(f"Strategy 1 (CSS): Found {len(plus_icons)} plus icons")
            except Exception as e:
                print(f"Strategy 1 (CSS) failed: {e}")
            
            # Strategy 2: XPath selector if CSS fails
            if not plus_icons:
                try:
                    plus_icons = await self.page.query_selector_all(f"xpath={config.PLUS_ICON_XPATH}")
                    print(f"Strategy 2 (XPath): Found {len(plus_icons)} plus icons")
                except Exception as e:
                    print(f"Strategy 2 (XPath) failed: {e}")
            
            # Strategy 3: Alternative selectors if first ones fail
            if not plus_icons:
                alternative_selectors = [
                    "i[class*='plus']",
                    "i[class*='bx-plus']", 
                    "i[class*='fa-plus']",
                    "button[class*='expand']",
                    "[class*='expand']"
                ]
                
                for i, selector in enumerate(alternative_selectors, 3):
                    try:
                        plus_icons = await self.page.query_selector_all(selector)
                        if plus_icons:
                            print(f"Strategy {i}: Found {len(plus_icons)} elements with selector: {selector}")
                            break
                    except Exception as e:
                        print(f"Strategy {i} failed: {e}")
            
            # If still no icons found, let's see what's available
            if not plus_icons:
                print("No plus icons found. Let's debug the page structure...")
                
                # Look for any clickable elements that might be expand buttons
                clickable_elements = await self.page.query_selector_all("button, a, i, [onclick]")
                print(f"Found {len(clickable_elements)} potentially clickable elements")
                
                # Print some of their classes and text for debugging
                for i, elem in enumerate(clickable_elements[:10]):  # Show first 10
                    try:
                        classes = await elem.get_attribute("class") or "no-class"
                        text = (await elem.text_content())[:50] if await elem.text_content() else "no-text"
                        print(f"  Element {i+1}: class='{classes}', text='{text}'")
                    except:
                        pass
                
                print("Please check the page structure and update the selectors in config.py")
                return
            
            print(f"Found {len(plus_icons)} subjects to process")
            
            # Process each subject
            for index, icon in enumerate(plus_icons, 1):
                try:
                    print(f"\nProcessing subject {index}...")
                    
                    # Get the pre-extracted subject name
                    subject_name = "Subject"
                    if index <= len(self.subject_names):
                        subject_name = self.subject_names[index - 1]
                    else:
                        subject_name = f"Subject {index}"
                    
                    # Scroll to element to ensure it's visible
                    await icon.scroll_into_view_if_needed()
                    await self.page.wait_for_timeout(100)
                    
                    # Click the plus icon to expand attendance details
                    await icon.click()
                    print(f"  ✓ Expanded subject {index}")
                    
                    # Wait for content to load
                    await self.page.wait_for_timeout(300)
                    
                    # Extract conducted count
                    conducted = await self.extract_conducted_count(index)
                    
                    # Extract attended count
                    attended = await self.extract_attended_count(index)
                    
                    # Store the data
                    if conducted is not None and attended is not None:
                        self.conducted_list.append(conducted)
                        self.attended_list.append(attended)
                        print(f"  ✓ Subject {index} ({subject_name}): Conducted={conducted}, Attended={attended}")
                    else:
                        print(f"  ⚠ Subject {index} ({subject_name}): Could not extract data")
                    
                    # Small delay before next subject
                    await self.page.wait_for_timeout(100)
                
                except Exception as e:
                    print(f"  ✗ Error processing subject {index}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"✗ Error during attendance extraction: {str(e)}")
    
    async def extract_all_subject_names(self):
        """
        Extract all subject names from the page before clicking any plus icons.
        This ensures we get the correct mapping of subject names to positions.
        """
        print("📋 Pre-extracting all subject names...")
        self.subject_names = []
        
        try:
            # Look for all elements that contain subject information
            # These are typically div elements with col-lg-12 class
            subject_containers = await self.page.query_selector_all('.col-lg-12')
            
            for container in subject_containers:
                try:
                    text_content = await container.text_content()
                    if text_content and len(text_content.strip()) > 10:
                        text = text_content.strip()
                        
                        # Look for the course code pattern: NUMBERS+LETTERS+NUMBERS-SUBJECT_NAME
                        import re
                        # Pattern: digits, letters, digits, dash, then the subject name
                        match = re.search(r'\d{2}[A-Z]{4}\d{4}-([A-Z\s&]+)', text)
                        if match:
                            subject_name = match.group(1).strip()
                            # Clean up the subject name
                            subject_name = ' '.join(subject_name.split())
                            # Remove any trailing content that's not part of the name
                            lines = subject_name.split('\n')
                            if lines:
                                subject_name = lines[0].strip()
                            
                            if len(subject_name) > 3 and len(subject_name) < 50:
                                self.subject_names.append(subject_name)
                                print(f"  📝 Found subject: {subject_name}")
                                
                except Exception as e:
                    print(f"  ⚠ Error processing container: {e}")
                    continue
            
            # If we didn't find enough subjects with the regex, try a more flexible approach
            if len(self.subject_names) < 3:
                print("  🔍 Trying alternative extraction method...")
                self.subject_names = []
                
                for container in subject_containers:
                    try:
                        text_content = await container.text_content()
                        if text_content and '-' in text_content:
                            text = text_content.strip()
                            
                            # Look for any pattern with dash and numbers at the start
                            if any(char.isdigit() for char in text[:15]):
                                parts = text.split('-', 1)
                                if len(parts) > 1:
                                    subject_name = parts[1].strip()
                                    subject_name = ' '.join(subject_name.split())
                                    lines = subject_name.split('\n')
                                    if lines:
                                        subject_name = lines[0].strip()
                                    
                                    if len(subject_name) > 3 and len(subject_name) < 50:
                                        # Avoid duplicates
                                        if subject_name not in self.subject_names:
                                            self.subject_names.append(subject_name)
                                            print(f"  📝 Found subject (alt): {subject_name}")
                                            
                    except Exception as e:
                        continue
            
            print(f"  ✅ Extracted {len(self.subject_names)} subject names")
            
        except Exception as e:
            print(f"  ❌ Error extracting subject names: {e}")
            # Fallback: create generic names
            self.subject_names = []
    
    async def extract_conducted_count(self, subject_index):
        """
        Extract the 'Conducted' count for a subject.
        
        Args:
            subject_index (int): The index of the current subject
        
        Returns:
            int: The conducted count, or None if not found
        """
        print(f"    Looking for 'Conducted' count...")
        
        await self.page.wait_for_timeout(150)
        
        try:
            # Quick approach: get all conducted elements and find the visible one
            all_conducted = await self.page.query_selector_all("span[id*='lblClsCondID']")
            
            # Find the visible element with content
            for elem in reversed(all_conducted):  # Start from the end (most recent)
                try:
                    is_visible = await elem.is_visible()
                    if is_visible:
                        text = await elem.text_content()
                        if text and text.strip().isdigit():
                            result = int(text.strip())
                            if 1 <= result <= 50:  # Reasonable range
                                print(f"    ✓ Extracted conducted count: {result}")
                                return result
                except:
                    continue
            
            # Fallback: use the last element
            if all_conducted:
                text = await all_conducted[-1].text_content()
                if text and text.strip().isdigit():
                    result = int(text.strip())
                    print(f"    ✓ Extracted conducted count (fallback): {result}")
                    return result
                        
        except Exception as e:
            print(f"    Error in conducted count extraction: {e}")
        
        print(f"    ⚠ Could not find conducted count for subject {subject_index}")
        return None
    
    async def extract_attended_count(self, subject_index):
        """
        Extract the 'Attended' count for a subject.
        
        Args:
            subject_index (int): The index of the current subject
        
        Returns:
            int: The attended count, or None if not found
        """
        print(f"    Looking for 'Attended' count...")
        
        await self.page.wait_for_timeout(150)
        
        try:
            # Quick approach: get all attended elements and find the visible one
            all_attended = await self.page.query_selector_all("span[id*='lblClsAttID']")
            
            # Find the visible element with content
            for elem in reversed(all_attended):  # Start from the end (most recent)
                try:
                    is_visible = await elem.is_visible()
                    if is_visible:
                        text = await elem.text_content()
                        if text and text.strip():
                            text = text.strip()
                            
                            # Parse the attendance format: "P-12/E-1/L-0/MCR-0/R-0/Total-13"
                            if "Total-" in text:
                                import re
                                total_part = text.split("Total-")[1]
                                numbers = re.findall(r'\d+', total_part)
                                if numbers:
                                    result = int(numbers[0])
                                    print(f"    ✓ Extracted attended count from Total: {result}")
                                    return result
                            
                            # If it's just a number
                            elif text.isdigit():
                                num = int(text)
                                if 1 <= num <= 50:  # Reasonable range
                                    result = num
                                    print(f"    ✓ Extracted attended count: {result}")
                                    return result
                except:
                    continue
            
            # Fallback: use the last element
            if all_attended:
                text = await all_attended[-1].text_content()
                if text and "Total-" in text:
                    import re
                    total_part = text.split("Total-")[1]
                    numbers = re.findall(r'\d+', total_part)
                    if numbers:
                        result = int(numbers[0])
                        print(f"    ✓ Extracted attended count (fallback): {result}")
                        return result
                        
        except Exception as e:
            print(f"    Error in attended count extraction: {e}")
        
        print(f"    ⚠ Could not find attended count for subject {subject_index}")
        return None
    
    async def extract_subject_name(self, plus_icon, subject_index):
        """
        Extract the subject name from the element containing the plus icon.
        
        Args:
            plus_icon: The plus icon element
            subject_index (int): The index of the current subject
            
        Returns:
            str: The cleaned subject name (e.g., "DATA VISUALISATION" from "21JUGE1111-DATA VISUALISATION")
        """
        try:
            # Method 1: Find the subject name in the direct vicinity of the plus icon
            # Navigate up the DOM tree to find the container with subject text
            parent_container = plus_icon
            
            for level in range(6):  # Try going up multiple levels
                try:
                    # Look for text content in the current container
                    if parent_container:
                        # Check direct siblings and children for subject name
                        container_text = await parent_container.text_content()
                        if container_text and len(container_text.strip()) > 10:
                            text = container_text.strip()
                            # Look for the course code pattern
                            if '-' in text and any(char.isdigit() for char in text[:15]):
                                # Extract everything after the first dash
                                parts = text.split('-', 1)
                                if len(parts) > 1:
                                    subject_name = parts[1].strip()
                                    # Clean up any extra content (remove line breaks, extra spaces)
                                    subject_name = ' '.join(subject_name.split())
                                    # Remove any trailing content that's not part of the subject name
                                    # Stop at common separators
                                    for separator in ['\n', '  ', '   ', '    ']:
                                        if separator in subject_name:
                                            subject_name = subject_name.split(separator)[0].strip()
                                    
                                    if len(subject_name) > 3 and len(subject_name) < 50:  # Reasonable bounds
                                        print(f"    ✓ Extracted subject name: {subject_name}")
                                        return subject_name
                        
                        # Move to parent
                        parent_container = await parent_container.evaluate('element => element.parentElement')
                    
                except Exception as e:
                    print(f"    Level {level} failed: {e}")
                    # Try to continue with parent
                    try:
                        parent_container = await parent_container.evaluate('element => element.parentElement')
                    except:
                        break
            
            # Method 2: Find the specific row/container for this plus icon
            try:
                # Get the row containing this plus icon
                row_element = await plus_icon.evaluate('''
                    element => {
                        let current = element;
                        // Go up to find a row or container element
                        while (current && current.parentElement) {
                            if (current.classList.contains('row') || 
                                current.classList.contains('col-lg-12') ||
                                current.tagName === 'TR' ||
                                current.classList.contains('panel')) {
                                return current;
                            }
                            current = current.parentElement;
                        }
                        return current;
                    }
                ''')
                
                if row_element:
                    row_text = await row_element.text_content()
                    if row_text and '-' in row_text:
                        text = row_text.strip()
                        if any(char.isdigit() for char in text[:15]):
                            parts = text.split('-', 1)
                            if len(parts) > 1:
                                subject_name = parts[1].strip()
                                subject_name = ' '.join(subject_name.split())
                                # Take only the first meaningful part
                                lines = subject_name.split('\n')
                                if lines:
                                    subject_name = lines[0].strip()
                                
                                if len(subject_name) > 3 and len(subject_name) < 50:
                                    print(f"    ✓ Extracted subject name (row method): {subject_name}")
                                    return subject_name
                        
            except Exception as e:
                print(f"    Method 2 (row) failed: {e}")
            
            # Method 3: Try to match by finding all subject containers before any clicks
            try:
                # Get all elements that contain subject information
                subject_elements = await self.page.query_selector_all('.col-lg-12')
                
                # Filter to only those with course code patterns
                valid_subjects = []
                for elem in subject_elements:
                    try:
                        text = await elem.text_content()
                        if text and '-' in text and any(char.isdigit() for char in text[:15]):
                            # Check if this element is related to our plus icon by proximity
                            elem_position = await elem.bounding_box()
                            icon_position = await plus_icon.bounding_box()
                            
                            if elem_position and icon_position:
                                # Check if they're vertically close (same row)
                                vertical_distance = abs(elem_position['y'] - icon_position['y'])
                                if vertical_distance < 100:  # Within 100px vertically
                                    parts = text.split('-', 1)
                                    if len(parts) > 1:
                                        subject_name = parts[1].strip()
                                        subject_name = ' '.join(subject_name.split())
                                        lines = subject_name.split('\n')
                                        if lines:
                                            subject_name = lines[0].strip()
                                        
                                        if len(subject_name) > 3 and len(subject_name) < 50:
                                            print(f"    ✓ Extracted subject name (proximity): {subject_name}")
                                            return subject_name
                    except:
                        continue
                        
            except Exception as e:
                print(f"    Method 3 (proximity) failed: {e}")
                        
        except Exception as e:
            print(f"    Error extracting subject name for subject {subject_index}: {e}")
        
        # Fallback: return a generic name
        fallback_name = f"Subject {subject_index}"
        print(f"    ⚠ Using fallback subject name: {fallback_name}")
        return fallback_name

    def calculate_and_display_results(self):
        """
        Calculate total attendance statistics and display results.
        """
        print("\n" + "="*50)
        print("ATTENDANCE CALCULATION RESULTS")
        print("="*50)
        
        if not self.conducted_list or not self.attended_list:
            print("✗ No attendance data was extracted successfully")
            return
        
        # Calculate totals
        total_conducted = sum(self.conducted_list)
        total_attended = sum(self.attended_list)
        
        # Calculate percentage
        if total_conducted > 0:
            attendance_percentage = (total_attended / total_conducted) * 100
        else:
            attendance_percentage = 0
        
        # Display detailed breakdown
        print(f"\nSubject-wise Breakdown:")
        for i, (conducted, attended) in enumerate(zip(self.conducted_list, self.attended_list), 1):
            subject_percentage = (attended / conducted) * 100 if conducted > 0 else 0
            print(f"  Subject {i}: {attended}/{conducted} ({subject_percentage:.2f}%)")
        
        # Display final results
        print(f"\nFINAL RESULTS:")
        print(f"Overall Attendance: {attendance_percentage:.2f}%")
        print(f"Total Conducted: {total_conducted}")
        print(f"Total Attended: {total_attended}")
        
        # Attendance status using config thresholds
        if attendance_percentage >= config.GOOD_ATTENDANCE_THRESHOLD:
            print(f"✓ Attendance Status: GOOD (≥{config.GOOD_ATTENDANCE_THRESHOLD}%)")
        elif attendance_percentage >= config.WARNING_ATTENDANCE_THRESHOLD:
            print(f"⚠ Attendance Status: WARNING ({config.WARNING_ATTENDANCE_THRESHOLD}-{config.GOOD_ATTENDANCE_THRESHOLD-1}%)")
        else:
            print(f"✗ Attendance Status: CRITICAL (<{config.WARNING_ATTENDANCE_THRESHOLD}%)")
    
    async def cleanup(self):
        """
        Clean up resources and close the browser.
        """
        print("\nCleaning up...")
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        print("✓ Browser closed successfully")
    
    async def run(self):
        """
        Main execution method that orchestrates the entire attendance checking process.
        """
        try:
            print("Starting Jain University Attendance Checker (Playwright Version with Gemini AI)")
            print("=" * 80)
            
            # Step 1: Setup Gemini AI
            self.setup_gemini()
            
            # Step 2: Get credentials from user
            self.get_credentials()
            
            # Step 3: Setup browser
            await self.setup_browser()
            
            # Step 4: Perform automated login
            login_success = await self.automated_login()
            if not login_success:
                print("✗ Login failed. Please check your credentials and try again.")
                return
            
            # Step 5: Navigate to attendance page
            navigation_success = await self.navigate_to_attendance_page()
            if not navigation_success:
                print("✗ Failed to navigate to attendance page. Session may have expired.")
                return
            
            # Step 6: Extract attendance data
            await self.extract_attendance_data()
            
            # Step 7: Calculate and display results
            self.calculate_and_display_results()
            
        except KeyboardInterrupt:
            print("\n\nProcess interrupted by user")
        except Exception as e:
            print(f"\n✗ An error occurred: {str(e)}")
        finally:
            # Always cleanup
            await self.cleanup()


async def main():
    """
    Entry point of the application.
    Creates an instance of JainAttendanceChecker and runs it.
    """
    print("Jain University Attendance Checker (Playwright Version with Gemini AI)")
    print("======================================================================")
    print("This tool will help you check your attendance automatically.")
    print("Features:")
    print("- Automated captcha solving using Gemini AI")
    print("- Terminal-based credential input")
    print("- Full automation (no manual intervention required)")
    print()
    
    # Create and run the attendance checker
    checker = JainAttendanceChecker()
    await checker.run()


if __name__ == "__main__":
    asyncio.run(main())
