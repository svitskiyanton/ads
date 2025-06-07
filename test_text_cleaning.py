#!/usr/bin/env python3
"""
Test script for OpenAI text cleaning functionality
"""

import os
import sys
import json
from orbita_form_filler_v2 import OpenAIExtractor

def test_text_cleaning():
    """Test the text cleaning functionality"""
    
    # Sample ad text with emojis and special characters
    test_ad_text = """
    🏠 Продается квартира в центре Ришон-ле-Циона! 🌞
    
    📐 Площадь: ~80 м²
    🛏️ 3 комнаты
    💰 Цена: 2,500,000 ₪
    📍 Адрес: ул. Ротшильд, 15
    ✨ Полностью обставлена
    🚗 Парковка в цене
    
    תיאור בעברית: דירה מרווחת ויפה
    
    ⭐ Контакт: 050-123-4567
    """
    
    print("🧪 Testing OpenAI Text Cleaning...")
    print(f"Original text:\n{test_ad_text}")
    print("\n" + "="*50 + "\n")
    
    try:
        # Initialize OpenAI extractor
        extractor = OpenAIExtractor()
        
        # Extract parameters and clean text
        result = extractor.extract_parameters(test_ad_text)
        
        print("✅ OpenAI Processing Results:")
        print(f"Parameters: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if "cleaned_text" in result:
            print(f"\n📝 Cleaned text:\n{result['cleaned_text']}")
        else:
            print("⚠️ No cleaned text found in result")
            
    except Exception as e:
        print(f"❌ Error testing text cleaning: {e}")
        print("⚠️ Make sure OPENAI_API_KEY is configured in config.py")

if __name__ == "__main__":
    test_text_cleaning() 