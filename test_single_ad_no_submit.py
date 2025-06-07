#!/usr/bin/env python3
"""
Test script for single ad processing - based on orbita_form_filler_v2.py
Tests only the 'Ремез Членов' folder - STOPS before form submission for safety
"""

import os
import sys
import time
from orbita_form_filler_v2 import OrbitaFormFillerV2, GoogleDriveClient, OpenAIExtractor

def test_single_ad_no_submit():
    """Test processing of single ad folder 'Ремез Членов' without submitting"""
    
    TARGET_FOLDER_NAME = 'Ремез Членов'
    
    print(f"🧪 Testing single ad processing for folder: '{TARGET_FOLDER_NAME}'")
    print("⚠️ SAFE MODE: Will stop before form submission")
    print("="*60)
    
    # Initialize components
    drive_client = None
    
    try:
        # 1. Initialize Google Drive client
        print("🔗 Initializing Google Drive client...")
        drive_client = GoogleDriveClient()
        if not drive_client.authenticate():
            print("❌ Failed to authenticate with Google Drive")
            return False
            
        # 2. Get all ad folders
        print("📂 Getting ad folders from Google Drive...")
        ad_folders = drive_client.get_ad_folders()
        
        if not ad_folders:
            print("❌ No ad folders found")
            return False
            
        print(f"✅ Found {len(ad_folders)} total ad folders")
        
        # 3. Find the specific target folder
        target_folder = None
        for folder in ad_folders:
            if folder['name'] == TARGET_FOLDER_NAME:
                target_folder = folder
                break
                
        if not target_folder:
            print(f"❌ Target folder '{TARGET_FOLDER_NAME}' not found")
            print("Available folders:")
            for folder in ad_folders[:10]:  # Show first 10 folders
                print(f"   - {folder['name']}")
            return False
            
        print(f"✅ Found target folder: {target_folder['name']} (ID: {target_folder['id']})")
        
        # 4. Get folder contents
        print("📄 Getting folder contents...")
        folder_contents = drive_client.get_folder_contents(target_folder['id'])
        
        if not folder_contents:
            print("❌ Folder is empty or inaccessible")
            return False
            
        print(f"✅ Folder contents:")
        print(f"   📝 Documents: {len(folder_contents['documents'])}")
        print(f"   🖼️ Images: {len(folder_contents['images'])}")
        
        # 5. Download ad text
        if not folder_contents['documents']:
            print("❌ No documents found in folder")
            return False
            
        print("📥 Downloading ad text...")
        ad_text = ""
        for doc in folder_contents['documents']:
            print(f"   📄 Processing: {doc['name']}")
            text = drive_client.download_document_text(doc)
            if text:
                ad_text += text + "\n"
                
        if not ad_text.strip():
            print("❌ No text content found")
            return False
            
        print(f"✅ Ad text downloaded ({len(ad_text)} characters)")
        print(f"📝 Original text preview:\n{ad_text[:300]}...")
        print("-" * 40)
        
        # 6. Extract parameters with OpenAI
        print("🤖 Extracting parameters with OpenAI...")
        try:
            extractor = OpenAIExtractor()
            parameters = extractor.extract_parameters(ad_text)
            
            print("✅ Extracted parameters:")
            for key, value in parameters.items():
                if key == 'cleaned_text':
                    print(f"   📝 {key}:\n{value}")
                    print("-" * 40)
                else:
                    print(f"   🏠 {key}: {value}")
                    
        except Exception as e:
            print(f"⚠️ OpenAI extraction failed: {e}")
            parameters = {"cleaned_text": ad_text}  # Use original text as fallback
        
        # 7. Download images
        image_paths = []
        if folder_contents['images']:
            print(f"📥 Downloading {len(folder_contents['images'])} images...")
            for img in folder_contents['images'][:5]:  # Limit to 5 images
                print(f"   🖼️ Downloading: {img['name']}")
                img_path = drive_client.download_image(img['id'], img['name'])
                if img_path:
                    image_paths.append(img_path)
                    print(f"      ✅ Saved: {img_path}")
                else:
                    print(f"      ❌ Failed to download {img['name']}")
                    
        print(f"✅ Downloaded {len(image_paths)} images")
        
        # 8. Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY:")
        print(f"📂 Folder: {TARGET_FOLDER_NAME}")
        print(f"📝 Ad text length: {len(ad_text)} characters")
        print(f"🤖 Parameters extracted: {len([k for k in parameters.keys() if k != 'cleaned_text'])}")
        print(f"🖼️ Images downloaded: {len(image_paths)}")
        
        if 'cleaned_text' in parameters:
            print(f"🧹 Text was cleaned by OpenAI")
            
        print("\n✅ Data preparation complete!")
        print("⚠️ Form filling and submission skipped for safety")
        print("💡 Use test_single_ad.py to test full form submission")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Starting single ad test (no submission)...")
    success = test_single_ad_no_submit()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        
    print("\n" + "="*60)

if __name__ == "__main__":
    main() 