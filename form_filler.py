from playwright.sync_api import sync_playwright
import time

def fill_form():
    with sync_playwright() as p:
        # Launch browser (set headless=True to run without UI)
        browser = p.chromium.launch(headless=False, slow_mo=1000)  # slow_mo adds delay for visibility
        page = browser.new_page()
        
        try:
            # Navigate to your form URL
            # Replace with the actual URL of your form
            page.goto("https://example.com/your-form-url")
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            
            # Example form filling based on your screenshot:
            
            # 1. Select from dropdown (Board selection)
            # Find the dropdown by its selector and select an option
            page.select_option('select[name="board"]', 'some_value')  # Replace with actual values
            
            # 2. Select city dropdown  
            page.select_option('select[name="city"]', 'all_israel')  # Replace with actual values
            
            # 3. Fill text area
            page.fill('textarea[name="ad_text"]', '''Это пример текста объявления.
Здесь может быть описание товара или услуги.
Контактная информация и дополнительные детали.''')
            
            # 4. Upload photos (if needed)
            # Make sure to have actual photo files in your project directory
            # page.set_input_files('input[name="photo1"]', 'photo1.jpg')
            # page.set_input_files('input[name="photo2"]', 'photo2.jpg')
            
            # 5. Fill email field
            page.fill('input[name="email"]', 'your.email@example.com')
            
            # 6. Fill phone number
            page.select_option('select[name="phone_code"]', '02')  # Phone code dropdown
            page.fill('input[name="phone"]', '1234567')  # Phone number
            
            # 7. Check the agreement checkbox
            page.check('input[type="checkbox"]')
            
            # 8. Submit the form (uncomment when ready)
            # page.click('input[type="submit"]')
            
            # Wait to see the result
            print("Form filled successfully! Check the browser window.")
            time.sleep(5)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            
        finally:
            browser.close()

# Alternative version with specific URL and selectors
def fill_form_with_specific_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        try:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            
            # You can inspect the page to get exact selectors
            print("Page loaded. You can now inspect elements to get their selectors.")
            
            # Example of getting all form elements
            form_elements = page.query_selector_all('input, select, textarea')
            print(f"Found {len(form_elements)} form elements")
            
            # Wait before closing
            time.sleep(10)
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

# Utility function to generate selector code
def inspect_form(url):
    """
    This function helps you inspect a form and generate code for filling it
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto(url)
        page.wait_for_load_state('networkidle')
        
        # Get all form elements and their attributes
        form_elements = page.evaluate('''
            () => {
                const elements = document.querySelectorAll('input, select, textarea, button');
                return Array.from(elements).map(el => ({
                    tag: el.tagName.toLowerCase(),
                    type: el.type || '',
                    name: el.name || '',
                    id: el.id || '',
                    className: el.className || '',
                    placeholder: el.placeholder || '',
                    text: el.textContent?.trim() || ''
                }));
            }
        ''')
        
        print("Form elements found:")
        for i, element in enumerate(form_elements):
            print(f"{i+1}. {element}")
        
        input("Press Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    # Choose one of these options:
    
    # Option 1: Fill form with example URL
    # fill_form()
    
    # Option 2: Inspect a specific form to understand its structure
    # Replace with your actual form URL
    url = input("Enter the form URL: ")
    if url:
        inspect_form(url)
    else:
        print("No URL provided. Edit the script to add your form URL.") 