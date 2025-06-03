"""
Quick exploration of personal shared folder
"""

import sys
sys.path.append('.')

from orbita_form_filler_v2 import GoogleDriveClient

def explore_personal_folder():
    """Explore the Свитский О.Л shared folder"""
    print("🔍 EXPLORING PERSONAL SHARED FOLDER")
    print("=" * 40)
    
    client = GoogleDriveClient()
    
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    # ID of "Свитский О.Л" folder from previous search
    personal_folder_id = "1G3j4meuYZpL1E1y-MQwr_PM4lxYVVVrf"
    
    try:
        print(f"📂 Exploring folder: Свитский О.Л")
        print(f"   ID: {personal_folder_id}")
        
        # Get all contents (folders and files)
        query = f"parents in '{personal_folder_id}'"
        results = client.service.files().list(
            q=query, 
            fields="files(id, name, mimeType)",
            pageSize=100
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            print(f"\n✅ Found {len(files)} items:")
            
            folders = []
            docs = []
            images = []
            
            for file in files:
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    folders.append(file)
                    print(f"   📁 {file['name']} (ID: {file['id']})")
                elif file['mimeType'] == 'application/vnd.google-apps.document':
                    docs.append(file)
                    print(f"   📄 {file['name']} (Google Doc)")
                elif file['mimeType'].startswith('image/'):
                    images.append(file)
                    print(f"   🖼️ {file['name']} (Image)")
                else:
                    print(f"   📋 {file['name']} ({file['mimeType']})")
            
            # Look for Real estate folder
            real_estate_folders = [f for f in folders if 'real' in f['name'].lower() or 'estate' in f['name'].lower()]
            
            if real_estate_folders:
                print(f"\n🎯 FOUND REAL ESTATE FOLDERS:")
                for folder in real_estate_folders:
                    print(f"   ✅ {folder['name']} (ID: {folder['id']})")
                    
                    # Explore this folder
                    subfolder_query = f"parents in '{folder['id']}'"
                    subfolder_results = client.service.files().list(
                        q=subfolder_query,
                        fields="files(id, name, mimeType)"
                    ).execute()
                    
                    subfiles = subfolder_results.get('files', [])
                    if subfiles:
                        print(f"      📊 Contains {len(subfiles)} items:")
                        for subfile in subfiles[:10]:  # Show first 10
                            if subfile['mimeType'] == 'application/vnd.google-apps.folder':
                                print(f"         📁 {subfile['name']}")
                            else:
                                print(f"         📄 {subfile['name']}")
                        
                        # Update config suggestion
                        print(f"\n   📝 SUGGESTED CONFIG UPDATE:")
                        print(f"   GOOGLE_DRIVE_PATH = \"{folder['name']}\"")
                        
                        # Look for Rishon LeZion subfolders
                        rishon_folders = [sf for sf in subfiles if sf['mimeType'] == 'application/vnd.google-apps.folder' and ('rishon' in sf['name'].lower() or 'лецион' in sf['name'].lower())]
                        if rishon_folders:
                            rishon_folder = rishon_folders[0]
                            print(f"   🎯 Found city folder: {rishon_folder['name']}")
                            
                            # Check for sales folder
                            city_query = f"parents in '{rishon_folder['id']}'"
                            city_results = client.service.files().list(q=city_query, fields="files(id, name, mimeType)").execute()
                            city_files = city_results.get('files', [])
                            
                            sales_folders = [cf for cf in city_files if cf['mimeType'] == 'application/vnd.google-apps.folder' and ('sale' in cf['name'].lower() or 'продажа' in cf['name'].lower())]
                            if sales_folders:
                                sales_folder = sales_folders[0]
                                full_path = f"{folder['name']}/{rishon_folder['name']}/{sales_folder['name']}"
                                print(f"   ✅ COMPLETE PATH: {full_path}")
                                print(f"   📝 FINAL CONFIG: GOOGLE_DRIVE_PATH = \"{full_path}\"")
            
            # If no Real estate found, suggest using this folder
            if not real_estate_folders and folders:
                print(f"\n💡 ALTERNATIVE: Use any existing folder for testing:")
                for folder in folders[:3]:  # Show first 3
                    print(f"   📁 {folder['name']} - GOOGLE_DRIVE_PATH = \"{folder['name']}\"")
        else:
            print("❌ No files found in this folder")
            
    except Exception as e:
        print(f"❌ Error exploring folder: {e}")

if __name__ == "__main__":
    explore_personal_folder() 