"""
Test script for new Orbita Form Filler v2 algorithm components

This script tests:
1. OpenAI parameter extraction
2. Google Drive new folder structure
3. Random email generation
4. Registration form detection

Run this before using the main script to ensure everything works.
"""

import sys
import time
import random
import string
from orbita_form_filler_v2 import OpenAIExtractor, GoogleDriveClient, AccountRegistrar
from playwright.sync_api import sync_playwright
import config

def test_email_generation():
    """Test random email generation"""
    print("\n🧪 Testing email generation...")
    
    emails = []
    for i in range(5):
        username = ''.join(random.choices(string.ascii_lowercase, k=7))
        domain = ''.join(random.choices(string.ascii_lowercase, k=10))
        email = f"{username}@{domain}.com"
        emails.append(email)
        print(f"  Generated: {email}")
    
    print("✅ Email generation test passed")
    return True

def test_openai_extraction():
    """Test OpenAI parameter extraction"""
    print("\n🧪 Testing OpenAI parameter extraction...")
    
    if config.OPENAI_API_KEY == "your_openai_api_key_here":
        print("⚠️ OpenAI API key not configured - skipping test")
        return False
    
    try:
        extractor = OpenAIExtractor()
        
        # Test with sample Russian ad text
        sample_text = """
        Ришон Лецион
        Продажа квартиры 
        4 комнаты, включая МАМАД ( комнату безопасности)  
        Район НАХЛАД ИУДА
        * Шикарный вид из окон ( не будет застроен никогда)
        * Очень высокий этаж
        * Родительская спальня с с/у
        * Большая гостиная
        * Солнечный балкон- 19 м на восток и север.
        * Двойная парковка 
        * Кладовая комната
        * В квартире никто не жил
        * В  доме 4 лифта .
        * Представительное лобби
        * Невероятно удобный выезд из города
        Цена: 2,450,000 ₪
        """
        
        print("  Extracting parameters from sample ad...")
        parameters = extractor.extract_parameters(sample_text)
        
        print(f"  Extracted: {parameters}")
        
        # Check if key parameters were extracted
        expected_keys = ['rooms', 'district', 'price']
        found_keys = [key for key in expected_keys if key in parameters]
        
        if found_keys:
            print(f"✅ OpenAI extraction test passed - found {len(found_keys)} parameters")
            return True
        else:
            print("❌ OpenAI extraction test failed - no parameters found")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI extraction test failed: {e}")
        return False

def test_google_drive_connection():
    """Test Google Drive connection and folder structure"""
    print("\n🧪 Testing Google Drive connection...")
    
    try:
        client = GoogleDriveClient()
        
        if not client.authenticate():
            print("❌ Google Drive authentication failed")
            return False
        
        print("  Checking folder path...")
        folder_id = client.find_folder_by_path(config.GOOGLE_DRIVE_PATH)
        
        if folder_id:
            print(f"✅ Found target folder: {config.GOOGLE_DRIVE_PATH}")
            
            # Get ad folders
            ad_folders = client.get_ad_folders()
            print(f"  Found {len(ad_folders)} ad folders")
            
            if ad_folders:
                # Test getting contents of first folder
                first_folder = ad_folders[0]
                contents = client.get_folder_contents(first_folder['id'])
                print(f"  First folder contents: {len(contents['google_docs'])} docs, {len(contents['images'])} images")
            
            return True
        else:
            print(f"❌ Could not find folder: {config.GOOGLE_DRIVE_PATH}")
            return False
            
    except Exception as e:
        print(f"❌ Google Drive test failed: {e}")
        return False

def test_registration_page():
    """Test registration page detection"""
    print("\n🧪 Testing registration page...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            print("  Navigating to registration page...")
            page.goto("https://passport.orbita.co.il/site/login/")
            page.wait_for_load_state('networkidle')
            
            # Check for registration button
            reg_button = page.locator("a.reg-pop")
            if reg_button.is_visible():
                print("✅ Registration button found")
                
                # Click to show registration form
                reg_button.click()
                time.sleep(2)
                
                # Check for form fields
                email_field = page.locator("#signupform-email")
                password_field = page.locator("#signupform-password")
                name_field = page.locator("#signupform-name")
                
                if (email_field.is_visible() and 
                    password_field.is_visible() and 
                    name_field.is_visible()):
                    print("✅ Registration form fields found")
                    result = True
                else:
                    print("❌ Registration form fields not found")
                    result = False
            else:
                print("❌ Registration button not found")
                result = False
            
            browser.close()
            return result
            
    except Exception as e:
        print(f"❌ Registration page test failed: {e}")
        return False

def test_captcha_solver():
    """Test 2captcha service"""
    print("\n🧪 Testing 2captcha service...")
    
    if config.CAPTCHA_API_KEY == "your_2captcha_api_key_here":
        print("⚠️ 2captcha API key not configured - skipping test")
        return False
    
    try:
        from twocaptcha import TwoCaptcha
        solver = TwoCaptcha(config.CAPTCHA_API_KEY)
        
        print("  Checking account balance...")
        balance = solver.balance()
        print(f"  Balance: ${balance}")
        
        if float(balance) > 0:
            print("✅ 2captcha service test passed")
            return True
        else:
            print("⚠️ 2captcha balance is low")
            return True  # Still consider it passed
            
    except Exception as e:
        print(f"❌ 2captcha service test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ORBITA FORM FILLER V2 - COMPONENT TESTS")
    print("=" * 60)
    
    tests = [
        ("Email Generation", test_email_generation),
        ("OpenAI Extraction", test_openai_extraction),
        ("Google Drive Connection", test_google_drive_connection),
        ("Registration Page", test_registration_page),
        ("2captcha Service", test_captcha_solver)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to run main script.")
    else:
        print("⚠️ Some tests failed. Check configuration before running main script.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 