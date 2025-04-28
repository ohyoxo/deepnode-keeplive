import re
import os
import time
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
    page = context.new_page()
    
    try:
        # Navigate to DeepNote sign-in page
        page.goto("https://deepnote.com/sign-in")
        print("Navigated to DeepNote sign-in page")
        
        # Navigate to GitHub login
        page.get_by_text("Continue with GitHub").click()
        print("Navigated to GitHub login page")
        time.sleep(10)
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
        except TimeoutError:
            print("Sign in button not found or page navigation timeout, but continuing execution")
        
        # Navigate to specified URL if provided
        if url:
            try:
                page.goto(url)
                page.wait_for_load_state("domcontentloaded", timeout=30000)
                print(f"Navigated to {url}")
            except TimeoutError:
                print(f"Timeout when navigating to {url}, but continuing execution")
        
        # Click "Run" button if available
        try:
            run_button = page.get_by_text("Run", exact=True)
            run_button.wait_for(state="visible", timeout=10000)
            run_button.click()
            print("Clicked 'Run' button")
        except TimeoutError:
            print("'Run' button not found, app maybe stop")
        
        # Look for "Running 1 block" text
        time.sleep(10)
        try:
            running_text = page.get_by_text("Running 1 block")
            running_text.wait_for(state="visible", timeout=10000)
            running_text.click()
            print("app is Running")
        except TimeoutError:
            print("'app is not Running")
    
      
    finally:
        # Always close browser
        page.close()
        context.close()
        browser.close()
        print("Browser closed")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
