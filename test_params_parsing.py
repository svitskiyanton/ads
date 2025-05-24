#!/usr/bin/env python3
"""
Test script to verify params.txt parsing
"""

def parse_apartment_details(params_content):
    """Parse apartment details from params.txt content based on line positions"""
    details = {}
    try:
        lines = params_content.strip().split('\n')
        # Filter out empty lines for correct line indexing
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        print(f"🔍 Non-empty lines count: {len(non_empty_lines)}")
        for i, line in enumerate(non_empty_lines, 1):
            print(f"  Line {i}: '{line}'")
        
        # Parse according to specified line positions:
        # Line 2 - address
        if len(non_empty_lines) > 1:
            details['address'] = non_empty_lines[1]
            
        # Line 4 - rooms
        if len(non_empty_lines) > 3:
            details['rooms'] = non_empty_lines[3]
            
        # Line 6 - floor
        if len(non_empty_lines) > 5:
            details['floor'] = non_empty_lines[5]
            
        # Line 8 - furniture
        if len(non_empty_lines) > 7:
            details['furniture'] = non_empty_lines[7]
            
        # Line 10 - price
        if len(non_empty_lines) > 9:
            details['price'] = non_empty_lines[9]
            
        print(f"✅ Parsed apartment details: {details}")
        return details
        
    except Exception as e:
        print(f"❌ Error parsing apartment details: {e}")
        return details

def test_parsing():
    """Test the parsing with the local params.txt file"""
    try:
        with open('params.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 Raw params.txt content:")
        print("=" * 40)
        print(content)
        print("=" * 40)
        
        print("\n📋 Line by line breakdown:")
        lines = content.strip().split('\n')
        for i, line in enumerate(lines, 1):
            print(f"Line {i}: '{line.strip()}'")
        
        print("\n🔍 Parsing apartment details:")
        details = parse_apartment_details(content)
        
        print("\n📊 Mapped values for form fields:")
        if 'address' in details:
            print(f"  🏠 Address: '{details['address']}'")
        if 'rooms' in details:
            print(f"  🚪 Rooms: '{details['rooms']}'")
            # Map room values to option values
            room_mapping = {
                "1": "77", "1.5": "78", "2": "79", "2.5": "80",
                "3": "81", "3.5": "82", "4": "83", "4.5": "84",
                "5": "85", "5.5": "86", "6+": "87"
            }
            option_value = room_mapping.get(details['rooms'], "0")
            print(f"    → Option value: {option_value}")
            
        if 'floor' in details:
            print(f"  🏢 Floor: '{details['floor']}'")
            # Map floor values to option values
            floor_mapping = {
                "0": "57", "1": "58", "2": "59", "3": "60", "4": "61",
                "5": "62", "6": "63", "7": "64", "8": "65", "9": "66",
                "10+": "67"
            }
            option_value = floor_mapping.get(details['floor'], "0")
            print(f"    → Option value: {option_value}")
            
        if 'furniture' in details:
            print(f"  🛋️ Furniture: '{details['furniture']}'")
            # Map furniture values to option values
            furniture_mapping = {
                "да": "26", "нет": "27", "частично": "28"
            }
            option_value = furniture_mapping.get(details['furniture'].lower(), "0")
            print(f"    → Option value: {option_value}")
            
        if 'price' in details:
            print(f"  💰 Price: '{details['price']}'")
            
    except FileNotFoundError:
        print("❌ params.txt file not found!")
    except Exception as e:
        print(f"❌ Error testing parsing: {e}")

if __name__ == "__main__":
    print("🧪 PARAMS.TXT PARSING TEST")
    print("=" * 50)
    test_parsing() 