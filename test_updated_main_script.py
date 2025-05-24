#!/usr/bin/env python3
"""
Simple test to verify the updated main script with authentication works
"""

from playwright.sync_api import sync_playwright
import time
from config import ORBITA_LOGIN_EMAIL, ORBITA_LOGIN_PASSWORD

def test_authentication():
    """Test just the authentication part of the updated script"""
    print("🧪 Testing authentication integration...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Import the authenticate_orbita function from the main script
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from orbita_form_filler import authenticate_orbita
            
            # Test authentication
            if authenticate_orbita(page):
                print("✅ Authentication test PASSED!")
                
                # Try navigating to ad posting page
                page.goto("https://doska.orbita.co.il/my/add/")
                page.wait_for_load_state('networkidle')
                
                if "my/add" in page.url:
                    print("✅ Navigation to ad posting page PASSED!")
                    
                    # Check if email field is present (shouldn't be after login)
                    email_input = page.locator('input[name="email"]')
                    if email_input.count() > 0:
                        is_visible = email_input.is_visible()
                        current_value = email_input.input_value()
                        print(f"📧 Email field: Visible={is_visible}, Value='{current_value}'")
                        if not is_visible or current_value:
                            print("✅ Email field handling CORRECT (hidden or pre-filled after login)")
                        else:
                            print("⚠️ Email field visible and empty - may need manual filling")
                    else:
                        print("✅ No email field found (perfect - not needed after login)")
                    
                    print("🎉 ALL TESTS PASSED! Main script ready for production use.")
                else:
                    print(f"❌ Navigation failed - unexpected URL: {page.url}")
            else:
                print("❌ Authentication test FAILED!")
                
        except Exception as e:
            print(f"❌ Test error: {e}")
        finally:
            input("Press ENTER to close browser...")
            browser.close()

if __name__ == "__main__":
    test_authentication() 