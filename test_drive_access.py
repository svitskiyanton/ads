import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def test_drive_access():
    """Test Google Drive API access to diagnose the real issue"""
    try:
        # Test basic API access
        creds = Credentials.from_authorized_user_file('token.json')
        service = build('drive', 'v3', credentials=creds)

        print('🧪 Testing basic API access...')
        results = service.files().list(pageSize=1).execute()
        print('✅ Basic API access works')
        
        # Try to access the specific folder
        folder_id = '10S_kuvpNFkDH1ihWVt1_mcQdOd5oh8ZN'
        print(f'🧪 Testing folder access: {folder_id}')
        
        files = service.files().list(
            q=f"parents in '{folder_id}'",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            corpora='allDrives'
        ).execute()
        
        print(f'✅ Found {len(files["files"])} files in folder')
        
        # Show all file types to debug
        print(f'\n📁 All files in folder:')
        google_docs = []
        images = []
        others = []
        
        for file in files['files']:
            print(f'   📄 {file["name"]} | Type: {file["mimeType"]}')
            
            if file['mimeType'] == 'application/vnd.google-apps.document':
                google_docs.append(file)
            elif file['mimeType'].startswith('image/'):
                images.append(file)
            else:
                others.append(file)
        
        print(f'\n📊 File Summary:')
        print(f'   Google Docs: {len(google_docs)}')
        print(f'   Images: {len(images)}')
        print(f'   Others: {len(others)}')
        
        # If we found Google Docs, test the first one
        if google_docs:
            file = google_docs[0]
            print(f'\n🧪 Testing Google Doc: {file["name"]} (ID: {file["id"]})')
            
            # Test 1: Get metadata only
            try:
                doc_info = service.files().get(fileId=file['id']).execute()
                print(f'✅ Can access Google Doc metadata')
            except Exception as e:
                print(f'❌ Error accessing Google Doc metadata: {e}')
                return
            
            # Test 2: Try to export (this is where rate limit occurs)
            try:
                print('🧪 Testing export to text/plain...')
                request = service.files().export_media(
                    fileId=file['id'], 
                    mimeType='text/plain'
                )
                print('✅ Export request created successfully')
                
                # Try to execute the request
                content = request.execute()
                print(f'✅ Export successful! Content length: {len(content)} bytes')
                print(f'📄 First 100 chars: {content[:100]}...')
                
            except Exception as e:
                print(f'❌ Export failed: {e}')
                print(f'📊 Error type: {type(e).__name__}')
                if hasattr(e, 'resp'):
                    print(f'📊 HTTP status: {e.resp.status}')
        else:
            print('\n❌ No Google Docs found in folder')
            print('🔍 Looking for files that might be Google Docs with different MIME types...')
            
            for file in others:
                if 'document' in file['mimeType'].lower() or 'google' in file['mimeType'].lower():
                    print(f'   🤔 Potential Google Doc: {file["name"]} | {file["mimeType"]}')
                
    except Exception as e:
        print(f'❌ API Error: {e}')

if __name__ == "__main__":
    test_drive_access() 