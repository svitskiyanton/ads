"""
Test script for updated OpenAI extraction functionality
Tests improved area/address detection and price parsing with spaces/commas
"""

import os
import sys
from typing import Dict

# Add current directory to path to import the main module
sys.path.append('.')

def test_openai_extraction():
    """Test OpenAI extraction with various ad text samples"""
    
    # Import the OpenAI extractor class
    try:
        from orbita_form_filler_v2 import OpenAIExtractor
        import config
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure config.py exists with OPENAI_API_KEY configured")
        return False

    # Test cases with different area/address and price formats
    test_cases = [
        {
            "name": "Rishon LeZion district with spaced price",
            "text": """
            Продается 4-комнатная квартира в районе НАХЛАД ИУДА, Ришон-ле-Цион.
            3 этаж, полностью меблированная.
            Цена: 2 500 000 шекелей.
            Отличное состояние, близко к центру.
            """
        },
        {
            "name": "Street address with comma-separated price",
            "text": """
            Квартира 3.5 комнаты на улице Ротшильд 15, Ришон-ле-Цион.
            5 этаж из 8. Цена 1,800,000 ₪.
            Без мебели, требует ремонта.
            """
        },
        {
            "name": "Hebrew street with dot-separated price",
            "text": """
            Продам 5 комнат в РЕМЕЗ районе.
            На ул. Герцль, 2 этаж.
            Стоимость 3.200.000 шекелей.
            С мебелью, готова к заселению.
            """
        },
        {
            "name": "Mixed format with multiple areas",
            "text": """
            Квартира в центре Ришон-ле-Циона, рядом с НЕВЕ ДЕНЯ.
            4.5 комнаты, высокий этаж (8 из 10).
            Обставленная, цена 2 800 000.
            Улица Жаботинский, тихий район.
            """
        },
        {
            "name": "Price without separators",
            "text": """
            Продается квартира в КИРЬЯТ ГАОН.
            3 комнаты, 4 этаж.
            Цена 1750000 шекелей.
            Частично с мебелью.
            """
        },
        {
            "name": "Street without explicit district",
            "text": """
            Квартира на Бялик 28, Ришон-ле-Цион.
            2.5 комнаты, первый этаж.
            Стоимость 1 650 000 ₪.
            Требует обновления.
            """
        }
    ]
    
    print("🧪 Testing Updated OpenAI Extraction")
    print("=" * 60)
    
    try:
        extractor = OpenAIExtractor()
        print("✅ OpenAI Extractor initialized successfully")
        print()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"📋 Test {i}: {test_case['name']}")
            print("-" * 40)
            print("Input text:")
            print(test_case['text'].strip())
            print()
            
            # Test OpenAI extraction
            try:
                result = extractor.extract_parameters(test_case['text'])
                print("🤖 OpenAI extraction result:")
                for key, value in result.items():
                    print(f"   {key}: {value}")
                
                if not result:
                    print("   No parameters extracted")
                    
            except Exception as e:
                print(f"❌ OpenAI extraction failed: {e}")
                
                # Test fallback extraction
                print("🔄 Testing fallback extraction...")
                try:
                    fallback_result = extractor._fallback_extraction(test_case['text'])
                    print("🛠️ Fallback extraction result:")
                    for key, value in fallback_result.items():
                        print(f"   {key}: {value}")
                except Exception as fe:
                    print(f"❌ Fallback extraction also failed: {fe}")
            
            print()
            print("=" * 60)
            print()
            
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI Extractor: {e}")
        print("Make sure config.py has valid OPENAI_API_KEY")
        return False
    
    return True

def test_fallback_only():
    """Test only the fallback extraction method"""
    
    print("🛠️ Testing Fallback Extraction Only")
    print("=" * 60)
    
    # Create a mock extractor to test fallback
    class MockExtractor:
        def _fallback_extraction(self, ad_text: str) -> Dict[str, str]:
            """Copy of the updated fallback method"""
            import re
            parameters = {}
            
            # Extract rooms
            room_patterns = [
                r'(\d+(?:\.\d+)?)\s*комнат',
                r'(\d+)\s*к',
                r'(\d+)\s*room'
            ]
            for pattern in room_patterns:
                match = re.search(pattern, ad_text, re.IGNORECASE)
                if match:
                    parameters['rooms'] = match.group(1)
                    break
            
            # Extract district - expanded list with streets
            districts = ['НАХЛАД ИУДА', 'РЕМЕЗ', 'НЕВЕ ДЕНЯ', 'КИРЬЯТ ГАОН', 'РАМАТ ЭЛИЯУ', 'ЦЕНТР', 'СТАРЫЙ ГОРОД']
            streets = ['РОТШИЛЬД', 'ГЕРЦЛЬ', 'ЖАБОТИНСКИЙ', 'БЯЛИК', 'АХАД ХААМ', 'РОШ ПИНА', 'ВАЙЦМАН', 'БEN ГУРИОН', 'СОКОЛОВ']
            
            # Check districts first
            for district in districts:
                if district in ad_text.upper():
                    parameters['district'] = district
                    break
            
            # If no district found, check streets
            if 'district' not in parameters:
                for street in streets:
                    if street in ad_text.upper():
                        parameters['district'] = f"ул. {street}"
                        break
            
            # Extract price - improved to handle spaces and commas
            price_patterns = [
                r'(\d{1,3}(?:[,\s]\d{3})*)\s*₪',  # With shekel symbol
                r'(\d{1,3}(?:[,\s]\d{3})+)',      # Long numbers with separators (4+ digits total)
                r'(\d{7,})',                      # Very long numbers (7+ digits)
                r'(\d{4,6})',                     # Medium numbers (4-6 digits)
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, ad_text)
                if price_match:
                    price = price_match.group(1).replace(',', '').replace(' ', '')
                    # Only consider it a price if it's reasonable (between 100k and 10M shekels)
                    try:
                        price_num = int(price)
                        if 100000 <= price_num <= 10000000:
                            parameters['price'] = price
                            break
                    except ValueError:
                        continue
            
            return parameters
    
    extractor = MockExtractor()
    
    test_texts = [
        "Квартира 4 комнаты в НАХЛАД ИУДА, цена 2 500 000 ₪",
        "На улице Ротшильд, 3.5 комнат, стоимость 1,800,000",
        "РЕМЕЗ район, 5 комнат, цена 3.200.000 шекелей",
        "Центр города, ул. Герцль, 2 800 000",
        "Бялик 15, 1650000 шекелей"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"📋 Fallback Test {i}:")
        print(f"Text: {text}")
        result = extractor._fallback_extraction(text)
        print("Result:", result)
        print("-" * 40)

def main():
    """Main test function"""
    print("🚀 Starting OpenAI Extraction Tests")
    print("Testing improved area/address detection and price parsing")
    print()
    
    # Check if config exists
    try:
        import config
        if not hasattr(config, 'OPENAI_API_KEY') or config.OPENAI_API_KEY == "your_openai_api_key_here":
            print("⚠️ OpenAI API key not configured, testing fallback only")
            test_fallback_only()
        else:
            print("✅ OpenAI API key found, testing full functionality")
            success = test_openai_extraction()
            if not success:
                print("\n🔄 Falling back to testing extraction logic only...")
                test_fallback_only()
    except ImportError:
        print("❌ config.py not found, testing fallback only")
        test_fallback_only()
    
    print("\n🎯 Test completed!")
    print("Check the results above to verify:")
    print("✓ Area/address detection for Rishon LeZion")
    print("✓ Price extraction with spaces and commas")

if __name__ == "__main__":
    main() 