from playwright.sync_api import sync_playwright
import time
import os

def fill_orbita_local_test():
    """
    Simple test version that works with local page.html
    Uses dummy data - no Google Drive required
    """
    print("🧪 ORBITA FORM FILLER - SIMPLE LOCAL TEST")
    print("=" * 50)
    print("📁 Using local page.html file")
    print("📝 Using dummy test data")
    print("🔗 Will NOT submit to live website")
    print("=" * 50)

    # Dummy test data
    test_ads = [
        {
            'phone_number': '0501234567',
            'ad_text': 'Beautiful apartment for sale in Rishon LeZion\n\n3 rooms, 2nd floor, renovated, close to shopping centers and schools. Excellent condition!',
            'images': ['apartment1.jpg', 'apartment2.png']
        },
        {
            'phone_number': '0527891234',
            'ad_text': 'Luxury penthouse with amazing view\n\nSpaciuos penthouse, 4 rooms, terrace, parking, elevator. Perfect for families.',
            'images': ['penthouse1.jpg', 'penthouse2.jpg', 'penthouse3.png']
        }
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1500)  # Slower for better visibility
        page = browser.new_page()
        
        try:
            # Load local HTML file
            current_dir = os.getcwd()
            local_file_path = f"file://{current_dir}/page.html"
            print(f"\n🌐 Loading: {local_file_path}")
            
            page.goto(local_file_path)
            page.wait_for_load_state('networkidle')
            print("✅ Page loaded successfully")

            # Process each test ad
            for i, ad_data in enumerate(test_ads, 1):
                print(f"\n📁 Processing test ad {i}/{len(test_ads)}")
                print(f"📱 Phone: {ad_data['phone_number']}")
                
                success = fill_form_with_data(page, ad_data)
                
                if success:
                    print(f"✅ Successfully filled form for: {ad_data['phone_number']}")
                else:
                    print(f"❌ Failed to fill form for: {ad_data['phone_number']}")

                # Reload page for next ad (if there are more)
                if i < len(test_ads):
                    print(f"\n⏳ Reloading page for next ad...")
                    time.sleep(3)
                    page.reload()
                    page.wait_for_load_state('networkidle')

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("\n🏁 Test completed!")
            print("Press Enter to close browser...")
            input()
            browser.close()

def fill_form_with_data(page, ad_data):
    """Fill the form with provided ad data"""
    try:
        print(f"\n📝 Filling form for: {ad_data['phone_number']}")
        
        # Wait a bit for page to stabilize
        time.sleep(2)

        # 1. Board selection - 'Квартиры - продам'
        print("📋 Selecting board: Квартиры - продам")
        board_found = False
        
        # Try different selectors for board dropdown
        board_selectors = [
            'select[name="board"]',
            'select[id="board"]', 
            'select.board',
            'select:has(option:text("Квартиры"))',
            'select:has(option[value*="apartment"])',
        ]
        
        for selector in board_selectors:
            try:
                if page.locator(selector).count() > 0:
                    # Try selecting by visible text first
                    try:
                        page.select_option(selector, label='Квартиры - продам')
                        board_found = True
                        print("✅ Board selected by label")
                        break
                    except:
                        # Try selecting by value
                        try:
                            page.select_option(selector, value='apartments_sale')
                            board_found = True 
                            print("✅ Board selected by value")
                            break
                        except:
                            continue
            except:
                continue
        
        if not board_found:
            print("⚠️ Board dropdown not found, trying click method")
            try:
                page.click('text=Выберите доску')
                time.sleep(1)
                page.click('text=Квартиры')
                print("✅ Board selected via text click")
            except:
                print("❌ Could not select board")

        time.sleep(1)

        # 2. City selection - 'Ришон ле Цион'
        print("🏙️ Selecting city: Ришон ле Цион")
        city_found = False
        
        city_selectors = [
            'select[name="city"]',
            'select[id="city"]',
            'select.city',
            'select:has(option:text("Ришон"))',
        ]
        
        for selector in city_selectors:
            try:
                if page.locator(selector).count() > 0:
                    try:
                        page.select_option(selector, label='Ришон ле Цион')
                        city_found = True
                        print("✅ City selected by label")
                        break
                    except:
                        try:
                            page.select_option(selector, value='rishon')
                            city_found = True
                            print("✅ City selected by value")
                            break
                        except:
                            continue
            except:
                continue
        
        if not city_found:
            print("⚠️ City dropdown not found, trying click method")
            try:
                page.click('text=Выберите город')
                time.sleep(1)
                page.click('text=Ришон')
                print("✅ City selected via text click")
            except:
                print("❌ Could not select city")

        time.sleep(1)

        # 3. Ad text
        print("📝 Filling ad text")
        text_found = False
        
        text_selectors = [
            'textarea[name="ad_text"]',
            'textarea[id="ad_text"]',
            'textarea.ad-text',
            'textarea[name="text"]',
            'textarea[name="description"]',
            'textarea'
        ]
        
        for selector in text_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, ad_data['ad_text'])
                    text_found = True
                    print("✅ Ad text filled")
                    break
            except:
                continue
        
        if not text_found:
            print("⚠️ Ad text field not found")

        time.sleep(1)

        # 4. Images (simulate in test mode)
        print(f"🖼️ TEST MODE: Would upload {len(ad_data['images'])} images:")
        for img in ad_data['images']:
            print(f"   📎 {img}")

        time.sleep(1)

        # 5. Phone number
        print(f"📱 Processing phone: {ad_data['phone_number']}")
        
        # Extract prefix (first 2 digits)
        phone_prefix = ad_data['phone_number'][:2] if len(ad_data['phone_number']) >= 2 else "05"
        phone_number = ad_data['phone_number'][2:] if ad_data['phone_number'].startswith(phone_prefix) else ad_data['phone_number']
        
        # Phone prefix dropdown
        prefix_found = False
        prefix_selectors = [
            'select[name="phone_prefix"]',
            'select[id="phone_prefix"]',
            'select.phone-prefix',
            'select[name="prefix"]'
        ]
        
        for selector in prefix_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.select_option(selector, value=phone_prefix)
                    prefix_found = True
                    print(f"✅ Phone prefix selected: {phone_prefix}")
                    break
            except:
                continue
        
        if not prefix_found:
            print(f"⚠️ Phone prefix dropdown not found for: {phone_prefix}")

        # Phone number field
        phone_found = False
        phone_selectors = [
            'input[name="phone"]',
            'input[id="phone"]',
            'input[type="tel"]',
            'input.phone',
            'input[name="phone_number"]'
        ]
        
        for selector in phone_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, phone_number)
                    phone_found = True
                    print(f"✅ Phone number filled: {phone_number}")
                    break
            except:
                continue
        
        if not phone_found:
            print("⚠️ Phone number field not found")

        time.sleep(1)

        # 6. Agreement checkbox
        print("✅ Looking for agreement checkbox")
        checkbox_found = False
        
        checkbox_selectors = [
            'input[type="checkbox"][name*="agree"]',
            'input[type="checkbox"][name*="terms"]',
            'input[type="checkbox"][id*="agree"]',
            'input[type="checkbox"]',
        ]
        
        for selector in checkbox_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.check(selector)
                    checkbox_found = True
                    print("✅ Agreement checkbox checked")
                    break
            except:
                continue
        
        if not checkbox_found:
            print("⚠️ Agreement checkbox not found")

        time.sleep(1)

        # 7. Submit button (TEST MODE - just locate, don't click)
        print("🧪 TEST MODE: Looking for submit button")
        submit_found = False
        
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:text("Добавить")',
            'button:text("Submit")',
            '.submit-btn',
            'button.btn-submit'
        ]
        
        for selector in submit_selectors:
            try:
                if page.locator(selector).count() > 0:
                    print(f"✅ Found submit button: {selector}")
                    print("🧪 TEST MODE: Would click submit button here")
                    submit_found = True
                    break
            except:
                continue
        
        if not submit_found:
            print("⚠️ Submit button not found")

        print(f"✅ Form filling completed for: {ad_data['phone_number']}")
        return True

    except Exception as e:
        print(f"❌ Error filling form: {e}")
        return False

if __name__ == "__main__":
    fill_orbita_local_test() 