import re
import os
import time
import json
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError

def run(playwright: Playwright) -> None:
    # Get credentials from environment variable
    try:
        credentials = os.environ.get('GT_PW', '')
        username, password = credentials.split(' ', 1)
    except ValueError:
        print("Error: GT_PW environment variable not set correctly. Format should be 'username password'")
        username, password = "", ""  # Set empty to continue script execution
    
    # Get URL from environment variable
    url = os.environ.get('DEEP_URL', '')
    if not url:
        print("Warning: DEEP_URL environment variable not set. Will not navigate after login.")
    
    # Launch browser
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context()
    
    # Define cookie file path
    cookie_file = Path("deepnote_cookies.json")
    
    # Load cookies if they exist
    cookie_login_successful = False
    if cookie_file.exists():
        try:
            with open(cookie_file, "r") as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            print("Loaded cookies from file")
            
            # Test if cookies work by navigating to sign-in page
            page = context.new_page()
            page.goto("https://deepnote.com/sign-in")
            print("Navigated to DeepNote sign-in page")
            
            # Wait to see if we get redirected to workspace
            try:
                page.wait_for_url("**/workspace/**", timeout=10000)
                current_url = page.url
                if re.match(r"https://deepnote.com/workspace/.*", current_url):
                    print("Cookie login successful, redirected to workspace")
                    cookie_login_successful = True
                else:
                    print("Cookie login may have failed, URL doesn't match workspace pattern")
            except TimeoutError:
                print("Cookie login failed, URL didn't change to workspace")
        except Exception as e:
            print(f"Error loading or using cookies: {str(e)}")
            page = context.new_page()
    else:
        print("No cookie file found, proceeding with password login")
        page = context.new_page()
    
    try:
        # If cookie login failed or no cookies existed, perform password login
        if not cookie_login_successful:
            if not page or page.is_closed():
                page = context.new_page()
            
            # Navigate to DeepNote sign-in page
            if page.url != "https://deepnote.com/sign-in":
                page.goto("https://deepnote.com/sign-in")
                print("Navigated to DeepNote sign-in page")
            
            # Navigate to GitHub login
            page.get_by_text("Continue with GitHub").click()
            print("Navigated to GitHub login page")
            time.sleep(5)
            
            # Wait for username field and enter credentials
            try:
                username_field = page.get_by_label("Username or email address")
                username_field.wait_for(state="visible", timeout=10000)
                username_field.click()
                username_field.fill(username)
                print("Entered username")
            except TimeoutError:
                print("Username field not found, but continuing execution")
            
            # Wait for password field and enter credentials
            try:
                password_field = page.get_by_label("Password")
                password_field.wait_for(state="visible", timeout=10000)
                password_field.click()
                password_field.fill(password)
                print("Entered password")
            except TimeoutError:
                print("Password field not found, but continuing execution")
            
            # Click sign in button
            try:
                sign_in_button = page.get_by_role("button", name="Sign in", exact=True)
                sign_in_button.wait_for(state="visible", timeout=10000)
                sign_in_button.click()
                print("Clicked sign in button")
                
                # Wait for navigation after login
                page.wait_for_load_state("networkidle", timeout=30000)
                print("Login completed and page loaded")
                try:
                   page.wait_for_url("**/workspace/**", timeout=10000)
                   current_url = page.url
                   if re.match(r"https://deepnote.com/workspace/.*", current_url):
                     print("login successful, redirected to workspace")
                     ookie_login_successful = True
                   else:
                     print("login may have failed, URL didn't change to workspace")
                except TimeoutError:
                   print("login may have failed, URL didn't change to workspace")
                # Save cookies after successful login
                cookies = context.cookies()
                with open(cookie_file, "w") as f:
                    json.dump(cookies, f)
                print("Saved cookies to file")
                
            except TimeoutError:
                print("Sign in button not found or page navigation timeout, but continuing execution")
        
        # Navigate to specified URL if provided
        if url:
            try:
                page.goto(url)
                page.wait_for_load_state("domcontentloaded", timeout=30000)
                print(f"Navigated to deepnode-url")
            except TimeoutError:
                print(f"Timeout when navigating to deepnode-url, but continuing execution")
        
        # Click "Run" button if available
        try:
            run_button = page.get_by_text("Run", exact=True)
            run_button.wait_for(state="visible", timeout=10000)
            run_button.click()
            print("Clicked 'Run' button")
        except TimeoutError:
            print("'Run' button not found, app maybe is Running")
        
        # Look for any text that starts with "Running"
        time.sleep(10)
        try:
            # Use locator with a more flexible selector - any text that starts with "Running"
            running_text_elements = page.locator("text=/^Running/")
            running_text_elements.first.wait_for(state="visible", timeout=10000)
            found_text = running_text_elements.first.text_content()
            print(f"Found running status: '{found_text}'")
            print("app is Running")
        except TimeoutError:
            print("app is not Running")
    
    finally:
        # Always close browser
        if page and not page.is_closed():
            page.close()
        context.close()
        browser.close()
        print("Browser closed")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
