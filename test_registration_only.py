#!/usr/bin/env python3
"""
Simple Registration Test Script
Tests only the registration process with retry logic to troubleshoot timeout issues.
"""

import time
from playwright.sync_api import sync_playwright
import config
from orbita_form_filler_v2 import AccountRegistrar

def test_registration_with_retries():
    """Test registration process with detailed logging"""
    print("=" * 60)
    print("🧪 TESTING REGISTRATION PROCESS WITH RETRIES")
    print("=" * 60)
    
    with sync_playwright() as p:
        print("🌐 Starting browser...")
        
        # Browser options with extended timeouts
        browser = p.chromium.launch(
            headless=False,
            timeout=config.BROWSER_LAUNCH_TIMEOUT,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-popup-blocking'
            ]
        )
        
        # Create context with permissions
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            permissions=['notifications'],
            ignore_https_errors=True
        )
        
        # Set timeouts
        context.set_default_timeout(config.PAGE_LOAD_TIMEOUT)
        
        page = context.new_page()
        page.set_default_timeout(config.PAGE_LOAD_TIMEOUT)
        
        try:
            print("✅ Browser started successfully")
            
            # Test registration with retries
            registrar = AccountRegistrar(page)
            success, email = registrar.register_account(max_attempts=config.MAX_REGISTRATION_ATTEMPTS)
            
            if success:
                print(f"🎉 REGISTRATION TEST PASSED!")
                print(f"📧 Email used: {email}")
            else:
                print(f"❌ REGISTRATION TEST FAILED after {config.MAX_REGISTRATION_ATTEMPTS} attempts")
            
            # Keep browser open for manual inspection
            input("\n⏸️ Press Enter to close browser and continue...")
            
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
        finally:
            browser.close()

def test_simple_page_load():
    """Test simple page loading without registration"""
    print("\n" + "=" * 60)
    print("🧪 TESTING SIMPLE PAGE LOAD")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, timeout=60000)
        context = browser.new_context()
        context.set_default_timeout(60000)
        page = context.new_page()
        
        try:
            print("🌐 Loading Orbita login page...")
            page.goto("https://passport.orbita.co.il/site/login/", timeout=60000)
            page.wait_for_load_state('networkidle', timeout=60000)
            
            print("✅ Page loaded successfully!")
            print(f"📍 Current URL: {page.url}")
            print(f"📄 Page title: {page.title()}")
            
            # Check for registration button
            reg_button = page.locator("a.reg-pop")
            if reg_button.is_visible():
                print("✅ Registration button found")
            else:
                print("❌ Registration button not found")
            
            input("\n⏸️ Press Enter to close browser and continue...")
            
        except Exception as e:
            print(f"❌ Simple page load failed: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    print("🚀 Starting registration tests...")
    
    # Test 1: Simple page load
    test_simple_page_load()
    
    # Test 2: Full registration with retries
    test_registration_with_retries()
    
    print("\n" + "=" * 60)
    print("🏁 ALL TESTS COMPLETED")
    print("=" * 60) 