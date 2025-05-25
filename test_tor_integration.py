#!/usr/bin/env python3
"""
Test script to verify Tor IP changing integration
This will test:
1. Tor initialization
2. IP checking
3. IP changing
4. Browser proxy configuration
"""

import time
from playwright.sync_api import sync_playwright
from orbita_form_filler import TorIPChanger
from config import USE_TOR_IP_ROTATION, TOR_IP_CHANGE_INTERVAL, TOR_STARTUP_DELAY, TOR_IP_CHANGE_DELAY

def test_tor_integration():
    """Test Tor IP changing functionality"""
    print("🧪 Testing Tor IP Changer Integration")
    print("=" * 50)
    
    if not USE_TOR_IP_ROTATION:
        print("⚠️ Tor IP rotation is disabled in config.py")
        print("Set USE_TOR_IP_ROTATION = True to test")
        return
    
    # Initialize Tor
    print("🔧 Step 1: Initializing Tor...")
    tor_changer = TorIPChanger()
    
    if not tor_changer.initialize_tor():
        print("❌ Failed to initialize Tor")
        return
    
    print("✅ Tor initialization successful")
    
    # Start Tor
    print("\n🔄 Step 2: Starting Tor service...")
    if not tor_changer.start_tor():
        print("❌ Failed to start Tor service")
        return
    
    print("✅ Tor service started")
    time.sleep(TOR_STARTUP_DELAY)
    
    # Get initial IP
    print(f"\n🌐 Step 3: Getting initial IP address...")
    initial_ip = tor_changer.get_current_ip()
    if initial_ip:
        print(f"✅ Initial IP: {initial_ip}")
    else:
        print("⚠️ Could not verify initial IP")
    
    # Test IP changing
    print(f"\n🔄 Step 4: Testing IP change...")
    if tor_changer.change_ip():
        time.sleep(TOR_IP_CHANGE_DELAY)
        new_ip = tor_changer.get_current_ip()
        if new_ip and new_ip != initial_ip:
            print(f"✅ IP successfully changed: {initial_ip} → {new_ip}")
        elif new_ip:
            print(f"⚠️ IP change attempted but same IP: {new_ip}")
        else:
            print("⚠️ Could not verify new IP")
    else:
        print("❌ Failed to change IP")
    
    # Test browser integration
    print(f"\n🌐 Step 5: Testing browser proxy integration...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            # Configure context with Tor proxy
            context_options = {
                'viewport': {'width': 1366, 'height': 768},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Add Tor proxy
            proxy_config = tor_changer.configure_browser_proxy(None)
            if proxy_config:
                context_options['proxy'] = proxy_config
                print("✅ Tor proxy configured for browser")
            
            context = browser.new_context(**context_options)
            page = context.new_page()
            
            # Test browsing with proxy
            print("🔍 Testing website access through Tor...")
            try:
                page.goto("https://httpbin.org/ip", timeout=15000)
                page.wait_for_load_state('networkidle')
                
                # Get IP shown on page
                page_content = page.content()
                if '"origin"' in page_content:
                    print("✅ Successfully accessed website through Tor proxy")
                    print(f"🌐 Page content indicates IP usage")
                else:
                    print("⚠️ Website accessed but IP verification unclear")
                    
            except Exception as e:
                print(f"❌ Error accessing website through Tor: {e}")
            
            print("📸 Browser will stay open for 10 seconds for manual inspection...")
            time.sleep(10)
            browser.close()
            
    except Exception as e:
        print(f"❌ Browser proxy test failed: {e}")
    
    # Cleanup
    print(f"\n🛑 Step 6: Cleaning up...")
    tor_changer.stop_tor()
    print("✅ Tor stopped")
    
    print(f"\n🎉 Tor integration test completed!")
    print(f"📋 Configuration:")
    print(f"   USE_TOR_IP_ROTATION: {USE_TOR_IP_ROTATION}")
    print(f"   TOR_IP_CHANGE_INTERVAL: {TOR_IP_CHANGE_INTERVAL}")
    print(f"   TOR_STARTUP_DELAY: {TOR_STARTUP_DELAY}")
    print(f"   TOR_IP_CHANGE_DELAY: {TOR_IP_CHANGE_DELAY}")

if __name__ == "__main__":
    test_tor_integration() 