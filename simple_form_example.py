from playwright.sync_api import sync_playwright

def simple_form_fill():
    """
    Simple example of form filling with Playwright
    """
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Change to True to run without opening browser window
        page = browser.new_page()
        
        # Replace with your actual form URL
        url = "YOUR_FORM_URL_HERE"
        page.goto(url)
        
        # Wait for page to load completely
        page.wait_for_load_state('networkidle')
        
        # Basic form interactions:
        
        # 1. Fill text input
        page.fill('input[name="username"]', 'my_username')
        
        # 2. Fill textarea
        page.fill('textarea', 'This is my message text')
        
        # 3. Select dropdown option
        page.select_option('select[name="category"]', 'option_value')
        
        # 4. Check checkbox
        page.check('input[type="checkbox"]')
        
        # 5. Upload file
        # page.set_input_files('input[type="file"]', 'path/to/file.jpg')
        
        # 6. Click submit button
        # page.click('button[type="submit"]')
        
        # Keep browser open for 5 seconds to see the result
        page.wait_for_timeout(5000)
        
        browser.close()

if __name__ == "__main__":
    simple_form_fill() 