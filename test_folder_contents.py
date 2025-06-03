#!/usr/bin/env python3
"""
Test script to inspect Google Drive folder contents
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def setup_drive_api():
    """Setup Google Drive API authentication"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            flow.redirect_uri = 'http://localhost:8080/callback'
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"🔗 Please visit: {auth_url}")
            
            code = input("📝 Enter authorization code: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('drive', 'v3', credentials=creds)
    print("✅ Google Drive API connected successfully!")
    return service

def find_folder_by_path(service, path):
    """Find folder ID by path"""
    path_parts = [p.strip() for p in path.split('/') if p.strip()]
    current_folder_id = 'root'
    
    for part in path_parts:
        print(f"🔍 Searching for folder: '{part}' in parent: {current_folder_id}")
        
        query = f"name='{part}' and parents in '{current_folder_id}' and mimeType='application/vnd.google-apps.folder'"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])
        
        if folders:
            current_folder_id = folders[0]['id']
            print(f"   ✅ Found: {part}")
        else:
            print(f"❌ Could not find folder: '{part}'")
            return None
    
    print(f"✅ Successfully found path '{path}' with ID: {current_folder_id}")
    return current_folder_id

def inspect_folder_contents(service, folder_id, folder_name):
    """Inspect all files in a folder"""
    print(f"\n📂 Inspecting folder: {folder_name}")
    print("=" * 50)
    
    query = f"parents in '{folder_id}'"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, size)"
    ).execute()
    
    files = results.get('files', [])
    print(f"📊 Found {len(files)} files")
    
    if not files:
        print("❌ No files found in this folder")
        return
    
    # Categorize files
    google_docs = []
    images = []
    other_files = []
    
    for file in files:
        print(f"\n📄 File: {file['name']}")
        print(f"   🏷️ MIME Type: {file['mimeType']}")
        print(f"   🆔 ID: {file['id']}")
        if 'size' in file:
            print(f"   📏 Size: {file['size']} bytes")
        
        if file['mimeType'] == 'application/vnd.google-apps.document':
            google_docs.append(file)
            print("   ✅ This is a Google Doc!")
        elif file['mimeType'].startswith('image/'):
            images.append(file)
            print("   🖼️ This is an image!")
        else:
            other_files.append(file)
            print("   ❓ Other file type")
    
    print(f"\n📊 Summary for {folder_name}:")
    print(f"   📝 Google Docs: {len(google_docs)}")
    print(f"   🖼️ Images: {len(images)}")
    print(f"   📄 Other files: {len(other_files)}")
    
    if google_docs:
        print("\n✅ Google Docs found:")
        for doc in google_docs:
            print(f"   📝 {doc['name']} (ID: {doc['id']})")
    else:
        print("\n❌ No Google Docs found!")
        if other_files:
            print("🔍 Other files that might be text:")
            for file in other_files:
                if any(ext in file['name'].lower() for ext in ['.txt', '.doc', '.docx']):
                    print(f"   📄 {file['name']} - {file['mimeType']}")

def main():
    print("🔍 GOOGLE DRIVE FOLDER CONTENT INSPECTOR")
    print("=" * 50)
    
    # Setup API
    service = setup_drive_api()
    
    # Find the ПРОДАЖА folder
    path = "Real estate/Ришон Лецион/ПРОДАЖА"
    parent_folder_id = find_folder_by_path(service, path)
    
    if not parent_folder_id:
        print("❌ Could not find ПРОДАЖА folder")
        return
    
    # Get all ad folders
    query = f"parents in '{parent_folder_id}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query).execute()
    folders = results.get('files', [])
    
    print(f"\n✅ Found {len(folders)} ad folders")
    
    # Inspect first few folders
    max_folders_to_check = 3
    print(f"\n🔍 Inspecting first {max_folders_to_check} folders:")
    
    for i, folder in enumerate(folders[:max_folders_to_check]):
        inspect_folder_contents(service, folder['id'], folder['name'])
        if i < max_folders_to_check - 1:
            input("\nPress Enter to continue to next folder...")

if __name__ == "__main__":
    main() 