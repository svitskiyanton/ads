# Example: How Google Drive authentication works in the script

"""
When you run the script:

1. Script looks for credentials.json (your OAuth2 credentials)
2. If token.json exists (saved login), uses it
3. If no token.json or expired:
   - Opens browser automatically
   - You sign in to Google
   - You grant permission to access your Drive
   - Script saves token.json for future use

NO MANUAL TOKEN INPUT NEEDED!
"""

# This is what happens in the background:
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None
    
    # Step 1: Check if we have saved credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Step 2: If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # First time login - opens browser
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # <- Browser opens here
        
        # Step 3: Save credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds 