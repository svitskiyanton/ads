#!/usr/bin/env python3
"""
Test script for enhanced security workflow:
1. Login
2. Process ad (simulated)
3. Logout  
4. Wait 3 minutes (shortened for testing)
5. Change IP
6. Re-login
7. Repeat
"""

import time
from playwright.sync_api import sync_playwright
from orbita_form_filler import authenticate_orbita, logout_orbita, TorIPChanger
from config import (
    LOGOUT_BETWEEN_ADS, WAIT_AFTER_LOGOUT, CHANGE_IP_AFTER_LOGOUT,
    USE_TOR_IP_ROTATION, TOR_IP_CHANGE_DELAY
)

def test_enhanced_workflow():
    """Test the enhanced security workflow"""
    print("🧪 Testing Enhanced Security Workflow")
    print("=" * 50)
    print("📋 Configuration:")
    print(f"   LOGOUT_BETWEEN_ADS: {LOGOUT_BETWEEN_ADS}")
    print(f"   WAIT_AFTER_LOGOUT: {WAIT_AFTER_LOGOUT} seconds")
    print(f"   CHANGE_IP_AFTER_LOGOUT: {CHANGE_IP_AFTER_LOGOUT}")
    print(f"   USE_TOR_IP_ROTATION: {USE_TOR_IP_ROTATION}")
    print("=" * 50)
    
    # Initialize Tor if enabled
    tor_changer = None
    if USE_TOR_IP_ROTATION and CHANGE_IP_AFTER_LOGOUT:
        print("🔧 Initializing Tor...")
        tor_changer = TorIPChanger()
        if tor_changer.initialize_tor():
            if tor_changer.start_tor():
                print(f"✅ Tor ready. Initial IP: {tor_changer.get_current_ip()}")
                time.sleep(3)
            else:
                print("⚠️ Tor failed to start")
                tor_changer = None
        else:
            print("⚠️ Tor initialization failed")
            tor_changer = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        
        # Configure context with Tor proxy if available
        context_options = {
            'viewport': {'width': 1366, 'height': 768},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if tor_changer and tor_changer.is_initialized:
            proxy_config = tor_changer.configure_browser_proxy(None)
            if proxy_config:
                context_options['proxy'] = proxy_config
                print("🌐 Browser configured to use Tor proxy")
        
        context = browser.new_context(**context_options)
        page = context.new_page()
        
        try:
            # Simulate processing 2 ads to test the workflow
            num_test_ads = 2
            
            for i in range(1, num_test_ads + 1):
                print(f"\n🎯 === TESTING AD {i}/{num_test_ads} ===")
                
                # Step 1: Authenticate
                print("🔐 Step 1: Authenticating...")
                if not authenticate_orbita(page):
                    print("❌ Authentication failed - stopping test")
                    break
                
                # Step 2: Simulate ad processing
                print("📝 Step 2: Simulating ad posting...")
                page.goto("https://doska.orbita.co.il/my/add/")
                page.wait_for_load_state('networkidle')
                print("✅ Ad page loaded (simulating successful ad posting)")
                time.sleep(2)
                
                # Enhanced security workflow (if not the last ad)
                if i < num_test_ads:
                    print("\n🔄 Step 3: Starting enhanced security workflow...")
                    
                    # Sub-step 1: Logout
                    if LOGOUT_BETWEEN_ADS:
                        print("🚪 Sub-step 1: Logging out...")
                        logout_success = logout_orbita(page)
                        if logout_success:
                            print("✅ Logout successful")
                        else:
                            print("⚠️ Logout failed")
                    
                    # Sub-step 2: Wait (shortened for testing)
                    test_wait_time = min(60, WAIT_AFTER_LOGOUT)  # Max 1 minute for testing
                    print(f"⏳ Sub-step 2: Waiting {test_wait_time} seconds (shortened for testing)...")
                    
                    # Show countdown
                    for remaining in range(test_wait_time, 0, -10):
                        print(f"⏰ {remaining} seconds remaining...")
                        time.sleep(min(10, remaining))
                    
                    print("✅ Wait completed")
                    
                    # Sub-step 3: Change IP
                    if CHANGE_IP_AFTER_LOGOUT and tor_changer:
                        print("🔄 Sub-step 3: Changing IP...")
                        old_ip = tor_changer.get_current_ip()
                        if tor_changer.change_ip():
                            new_ip = tor_changer.get_current_ip()
                            print(f"✅ IP changed: {old_ip} → {new_ip}")
                            time.sleep(TOR_IP_CHANGE_DELAY)
                        else:
                            print("⚠️ IP change failed")
                    elif CHANGE_IP_AFTER_LOGOUT:
                        print("⚠️ IP change requested but Tor not available")
                    else:
                        print("ℹ️ IP change disabled")
                    
                    print("✅ Enhanced security workflow completed")
            
            print(f"\n🎉 Enhanced workflow test completed!")
            print("📋 Summary:")
            print(f"   - Tested {num_test_ads} ad cycles")
            print(f"   - Logout between ads: {'✅' if LOGOUT_BETWEEN_ADS else '❌'}")
            print(f"   - IP changing: {'✅' if (CHANGE_IP_AFTER_LOGOUT and tor_changer) else '❌'}")
            print(f"   - Wait periods: {'✅' if WAIT_AFTER_LOGOUT > 0 else '❌'}")
            
            print("\n📸 Browser staying open for 15 seconds for inspection...")
            time.sleep(15)
            
        except Exception as e:
            print(f"❌ Test error: {e}")
        finally:
            if tor_changer:
                tor_changer.stop_tor()
            browser.close()

if __name__ == "__main__":
    test_enhanced_workflow() 