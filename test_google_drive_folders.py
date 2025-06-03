"""
Google Drive Folder Explorer
Test script to find accessible folders and handle shared folders
"""

import os
import sys
import urllib.parse
sys.path.append('.')

from orbita_form_filler_v2 import GoogleDriveClient

def test_drive_folders():
    """Test and explore Google Drive folder structure"""
    print("🔍 GOOGLE DRIVE FOLDER EXPLORER")
    print("=" * 50)
    
    try:
        client = GoogleDriveClient()
        
        if not client.authenticate():
            print("❌ Authentication failed")
            return
        
        print("✅ Authenticated successfully")
        print("\n📁 Exploring accessible folders...")
        
        # COMPREHENSIVE SEARCH FOR "Real estate"
        print("\n🎯 COMPREHENSIVE SEARCH FOR 'Real estate':")
        target_folder = "Real estate"
        found_folders = []
        
        # Strategy 1: Direct search with original name
        print(f"\n1️⃣ Direct search for '{target_folder}':")
        try:
            query = f"name='{target_folder}' and mimeType='application/vnd.google-apps.folder'"
            results = client.service.files().list(
                q=query, 
                fields="files(id, name, parents, owners)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                corpora='allDrives'
            ).execute()
            folders = results.get('files', [])
            
            if folders:
                for folder in folders:
                    print(f"   ✅ FOUND: {folder['name']} (ID: {folder['id']})")
                    found_folders.append(folder)
            else:
                print(f"   ❌ Not found with direct search")
                
        except Exception as e:
            print(f"   ❌ Direct search error: {e}")
        
        # Strategy 2: Search in shared folders
        print(f"\n2️⃣ Search in shared folders:")
        try:
            query = f"name='{target_folder}' and sharedWithMe=true and mimeType='application/vnd.google-apps.folder'"
            results = client.service.files().list(
                q=query, 
                fields="files(id, name, parents, owners)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                corpora='allDrives'
            ).execute()
            folders = results.get('files', [])
            
            if folders:
                for folder in folders:
                    owner_name = folder.get('owners', [{}])[0].get('displayName', 'Unknown')
                    print(f"   ✅ FOUND: {folder['name']} (ID: {folder['id']}) - Owner: {owner_name}")
                    found_folders.append(folder)
            else:
                print(f"   ❌ Not found in shared folders")
                
        except Exception as e:
            print(f"   ❌ Shared search error: {e}")
        
        # Strategy 3: Partial search with contains
        print(f"\n3️⃣ Partial search (contains 'Real'):")
        try:
            query = f"name contains 'Real' and mimeType='application/vnd.google-apps.folder'"
            results = client.service.files().list(
                q=query, 
                fields="files(id, name, parents, owners)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                corpora='allDrives'
            ).execute()
            folders = results.get('files', [])
            
            if folders:
                for folder in folders:
                    print(f"   🔍 Found: {folder['name']} (ID: {folder['id']})")
                    if folder['name'] == target_folder:
                        print(f"   ✅ EXACT MATCH!")
                        found_folders.append(folder)
            else:
                print(f"   ❌ No folders containing 'Real'")
                
        except Exception as e:
            print(f"   ❌ Partial search error: {e}")
        
        # Strategy 4: List ALL folders and manually search
        print(f"\n4️⃣ Manual search through ALL folders:")
        try:
            all_queries = [
                "parents in 'root' and mimeType='application/vnd.google-apps.folder'",
                "sharedWithMe=true and mimeType='application/vnd.google-apps.folder'"
            ]
            
            all_found_folders = []
            
            for i, query in enumerate(all_queries):
                location = "Root" if i == 0 else "Shared"
                print(f"   📂 Searching in {location} folders...")
                
                results = client.service.files().list(
                    q=query, 
                    fields="files(id, name, parents, owners)",
                    pageSize=1000,  # Get more results
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    corpora='allDrives'
                ).execute()
                
                folders = results.get('files', [])
                print(f"   📊 Found {len(folders)} folders in {location}")
                
                for folder in folders:
                    folder_name = folder['name']
                    
                    # Check for various matches
                    if (folder_name == target_folder or 
                        'real' in folder_name.lower() or 
                        'estate' in folder_name.lower() or
                        'property' in folder_name.lower() or
                        'ad' in folder_name.lower()):
                        
                        owner_info = ""
                        if 'owners' in folder:
                            owner_name = folder.get('owners', [{}])[0].get('displayName', 'Unknown')
                            owner_info = f" - Owner: {owner_name}"
                        
                        match_type = "EXACT" if folder_name == target_folder else "SIMILAR"
                        print(f"   🎯 {match_type}: '{folder_name}' (ID: {folder['id']}){owner_info}")
                        
                        if folder_name == target_folder:
                            found_folders.append(folder)
                        
                        all_found_folders.append(folder)
                
        except Exception as e:
            print(f"   ❌ Manual search error: {e}")
        
        # Strategy 5: Try different encoding approaches
        print(f"\n5️⃣ Testing different encodings:")
        encodings_to_try = [
            target_folder,
            urllib.parse.quote(target_folder),
            target_folder.encode('utf-8').decode('utf-8'),
        ]
        
        for encoding in encodings_to_try:
            try:
                if encoding != target_folder:
                    print(f"   🔄 Trying encoding: {encoding}")
                    query = f"name='{encoding}' and mimeType='application/vnd.google-apps.folder'"
                    results = client.service.files().list(
                        q=query, 
                        fields="files(id, name)",
                        includeItemsFromAllDrives=True,
                        supportsAllDrives=True,
                        corpora='allDrives'
                    ).execute()
                    folders = results.get('files', [])
                    
                    if folders:
                        for folder in folders:
                            print(f"   ✅ Found with encoding: {folder['name']} (ID: {folder['id']})")
                            found_folders.append(folder)
                            
            except Exception as e:
                print(f"   ⚠️ Encoding {encoding} failed: {e}")
        
        # Summary
        print(f"\n" + "="*50)
        print("📋 SEARCH RESULTS SUMMARY:")
        
        if found_folders:
            print(f"✅ Found {len(found_folders)} exact matches for '{target_folder}':")
            for folder in found_folders:
                owner_info = ""
                if 'owners' in folder:
                    owner_name = folder.get('owners', [{}])[0].get('displayName', 'Unknown')
                    owner_info = f" - Owner: {owner_name}"
                
                print(f"   📂 {folder['name']}")
                print(f"      ID: {folder['id']}")
                print(f"      {owner_info}")
                
                # Test if we can access subfolders
                try:
                    print(f"   🔍 Testing subfolder access...")
                    subfolder_query = f"parents in '{folder['id']}' and mimeType='application/vnd.google-apps.folder'"
                    subfolder_results = client.service.files().list(
                        q=subfolder_query, 
                        fields="files(id, name)",
                        includeItemsFromAllDrives=True,
                        supportsAllDrives=True,
                        corpora='allDrives'
                    ).execute()
                    subfolders = subfolder_results.get('files', [])
                    
                    if subfolders:
                        print(f"   ✅ Found {len(subfolders)} subfolders:")
                        for subfolder in subfolders[:5]:  # Show first 5
                            print(f"      📁 {subfolder['name']}")
                            
                        # Look for "Rishon LeZion" or similar
                        rishon_folders = [sf for sf in subfolders if 'rishon' in sf['name'].lower() or 'lezion' in sf['name'].lower() or 'цион' in sf['name'].lower()]
                        if rishon_folders:
                            rishon_folder = rishon_folders[0]
                            print(f"   🎯 Found Rishon LeZion folder: {rishon_folder['name']} (ID: {rishon_folder['id']})")
                            
                            # Check for SALES subfolder
                            sales_query = f"parents in '{rishon_folder['id']}' and mimeType='application/vnd.google-apps.folder'"
                            sales_results = client.service.files().list(
                                q=sales_query, 
                                fields="files(id, name)",
                                includeItemsFromAllDrives=True,
                                supportsAllDrives=True,
                                corpora='allDrives'
                            ).execute()
                            sales_folders = sales_results.get('files', [])
                            
                            for sf in sales_folders:
                                if 'sale' in sf['name'].lower() or 'продажа' in sf['name'].lower():
                                    print(f"   🎯 Found SALES folder: {sf['name']} (ID: {sf['id']})")
                                    final_path = f"{folder['name']}/{rishon_folder['name']}/{sf['name']}"
                                    print(f"   ✅ COMPLETE PATH FOUND: {final_path}")
                                    print(f"   📝 Update config.py with: GOOGLE_DRIVE_PATH = \"{final_path}\"")
                    else:
                        print(f"   ⚠️ No subfolders found or access denied")
                        
                except Exception as e:
                    print(f"   ❌ Subfolder access error: {e}")
                
                print()
        else:
            print(f"❌ No exact matches found for '{target_folder}'")
            print("📝 Suggestions:")
            print(f"   1. Check if the folder name is spelled exactly as '{target_folder}'")
            print("   2. Ensure you have proper access permissions to the folder")
            print("   3. The folder might be in a different location or have different sharing settings")
            print("   4. It may take a few minutes for the rename to propagate through Google's systems")
        
        print("="*50)
        
    except Exception as e:
        print(f"❌ Drive exploration failed: {e}")

if __name__ == "__main__":
    test_drive_folders() 