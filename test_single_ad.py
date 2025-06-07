#!/usr/bin/env python3
"""
Test script for single ad processing - based on orbita_form_filler_v2.py
Tests only the 'Ремез Членов' folder
"""

import os
import sys
import time
from orbita_form_filler_v2 import OrbitaFormFillerV2, GoogleDriveClient, OpenAIExtractor

def test_single_ad():
    """Test processing of single ad folder 'Ремез Членов'"""
    
    TARGET_PATH = ["Real estate", "Ришон Лецион", "ПРОДАЖА", "Ремез Членов"]
    
    print(f"🧪 Testing single ad processing for folder path: {' -> '.join(TARGET_PATH)}")
    print("="*60)
    
    # Initialize components
    filler = None
    drive_client = None
    
    try:
        # 1. Initialize Google Drive client
        print("🔗 Initializing Google Drive client...")
        drive_client = GoogleDriveClient()
        if not drive_client.authenticate():
            print("❌ Failed to authenticate with Google Drive")
            return False
            
        # 2. Navigate through the folder path
        print("📂 Navigating through folder path...")
        current_folder_id = 'root'
        
        for i, folder_name in enumerate(TARGET_PATH):
            print(f"🔍 Looking for folder: '{folder_name}'")
            
            # Search for folder in current location
            query = f"name='{folder_name}' and parents in '{current_folder_id}' and mimeType='application/vnd.google-apps.folder'"
            results = drive_client.service.files().list(
                q=query, 
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if not folders:
                print(f"❌ Folder '{folder_name}' not found in current location")
                
                # Show available folders at this level
                query_all = f"parents in '{current_folder_id}' and mimeType='application/vnd.google-apps.folder'"
                all_results = drive_client.service.files().list(
                    q=query_all, 
                    fields="files(id, name)"
                ).execute()
                available = all_results.get('files', [])
                
                print("Available folders at this level:")
                for folder in available[:10]:
                    print(f"   - {folder['name']}")
                return False
                
            current_folder_id = folders[0]['id']
            print(f"✅ Found: {folder_name} (ID: {current_folder_id})")
        
        # At this point, current_folder_id should be the "Ремез Членов" folder
        target_folder = {'id': current_folder_id, 'name': TARGET_PATH[-1]}
        print(f"✅ Successfully navigated to target folder: {target_folder['name']}")
        
        # 3. Get folder contents
        print("📄 Getting folder contents...")
        folder_contents = drive_client.get_folder_contents(target_folder['id'])
        
        if not folder_contents:
            print("❌ Folder is empty or inaccessible")
            return False
            
        print(f"✅ Folder contents:")
        print(f"   📝 Documents: {len(folder_contents['documents'])}")
        print(f"   🖼️ Images: {len(folder_contents['images'])}")
        
        # 4. Download ad text
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
        print(f"Preview: {ad_text[:200]}...")
        
        # 5. Extract parameters with OpenAI
        print("🤖 Extracting parameters with OpenAI...")
        try:
            extractor = OpenAIExtractor()
            parameters = extractor.extract_parameters(ad_text)
            
            print("✅ Extracted parameters:")
            for key, value in parameters.items():
                if key == 'cleaned_text':
                    print(f"   📝 {key}: {value[:100]}..." if len(value) > 100 else f"   📝 {key}: {value}")
                else:
                    print(f"   🏠 {key}: {value}")
                    
        except Exception as e:
            print(f"⚠️ OpenAI extraction failed: {e}")
            parameters = {"cleaned_text": ad_text}  # Use original text as fallback
        
        # 6. Download images
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
        
        # 7. Initialize form filler
        print("🌐 Initializing browser and form filler...")
        filler = OrbitaFormFillerV2()
        
        if not filler.initialize():
            print("❌ Failed to initialize form filler")
            return False
            
        if not filler.start_browser():
            print("❌ Failed to start browser")
            return False
            
        # 8. Register and login
        print("🔐 Registering and logging in...")
        success, email = filler.register_and_login()
        if not success:
            print("❌ Failed to register/login")
            return False
            
        print(f"✅ Logged in with email: {email}")
        
        # 9. Fill form (with submission enabled for testing)
        print("📝 Filling Orbita form...")
        
        # Temporarily comment out form submission for testing
        print("⚠️ NOTE: Form submission is enabled for this test")
        print("📝 Press Ctrl+C during form filling if you want to stop before submission")
        
        try:
            success = filler._fill_orbita_form(ad_text, parameters, image_paths)
            
            if success:
                print("🎉 SUCCESS! Ad was processed and submitted successfully!")
            else:
                print("❌ Form filling failed")
                
        except KeyboardInterrupt:
            print("\n⏹️ Test interrupted by user")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if filler:
            print("🧹 Cleaning up...")
            filler.cleanup()

def main():
    """Main function"""
    print("🚀 Starting single ad test...")
    success = test_single_ad()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        
    print("\n" + "="*60)

if __name__ == "__main__":
    main() 