#!/usr/bin/env python3
"""
IP Comparison Test - Shows real IP vs Tor IP
"""

import time
import requests
from orbita_form_filler import TorIPChanger

def check_real_ip():
    """Check IP without Tor"""
    print("🌐 Checking your REAL IP address (without Tor)...")
    try:
        response = requests.get("https://httpbin.org/ip", timeout=10)
        real_ip = response.json().get('origin', 'Unknown')
        print(f"📍 Your REAL IP: {real_ip}")
        return real_ip
    except Exception as e:
        print(f"❌ Error checking real IP: {e}")
        return None

def main():
    print("🧪 IP COMPARISON TEST")
    print("=" * 50)
    
    # Step 1: Check real IP
    print("Step 1: Checking your real IP address...")
    real_ip = check_real_ip()
    
    if real_ip:
        print(f"\n✅ Your real IP is: {real_ip}")
        print("🇮🇱 This is likely your Israeli ISP IP address")
    
    input("\nPress Enter to continue to Tor setup...")
    
    # Step 2: Initialize and start Tor
    print("\nStep 2: Setting up Tor...")
    tor_changer = TorIPChanger()
    
    if not tor_changer.initialize_tor():
        print("❌ Failed to initialize Tor")
        return
    
    print("✅ Tor initialized")
    
    if not tor_changer.start_tor():
        print("❌ Failed to start Tor")
        return
    
    print("✅ Tor is now running!")
    
    # Step 3: Check Tor IP
    print("\nStep 3: Checking IP through Tor...")
    tor_ip = tor_changer.get_current_ip()
    
    print(f"\n📊 COMPARISON RESULTS:")
    print(f"   🏠 Real IP:  {real_ip}")
    print(f"   🔒 Tor IP:   {tor_ip}")
    
    if real_ip and tor_ip and real_ip != tor_ip:
        print("✅ SUCCESS! Tor is providing a different IP address!")
    elif real_ip == tor_ip:
        print("⚠️ WARNING! Same IP - Tor might not be working properly")
    
    print(f"\n⏳ TOR IS NOW ACTIVE!")
    print(f"🌐 Your traffic is now routed through: {tor_ip}")
    print(f"📱 You can now check ipaddress.my in your browser")
    print(f"🔍 You should see: {tor_ip} (not {real_ip})")
    
    print(f"\n⏰ WAITING FOR YOU TO TEST...")
    print(f"📋 Instructions:")
    print(f"   1. Open your browser")
    print(f"   2. Go to ipaddress.my")
    print(f"   3. Verify you see: {tor_ip}")
    print(f"   4. Come back here when done")
    
    input(f"\nPress Enter when you've verified the IP in your browser...")
    
    # Test IP change
    print(f"\n🔄 Bonus: Testing IP change...")
    old_tor_ip = tor_ip
    if tor_changer.change_ip():
        new_tor_ip = tor_changer.get_current_ip()
        print(f"🎯 IP changed from {old_tor_ip} to {new_tor_ip}")
        print(f"🔄 You can refresh ipaddress.my to see the new IP: {new_tor_ip}")
        
        input(f"\nPress Enter to continue...")
    
    # Cleanup
    print(f"\n🛑 Stopping Tor...")
    tor_changer.stop_tor()
    print(f"✅ Tor stopped - you're back to your real IP: {real_ip}")
    
    print(f"\n🎉 Test completed!")
    print(f"📋 Summary:")
    print(f"   🏠 Your real IP: {real_ip}")
    print(f"   🔒 Tor provided: {tor_ip}")
    print(f"   ✅ Anonymization: {'Working' if real_ip != tor_ip else 'Failed'}")

if __name__ == "__main__":
    main() 