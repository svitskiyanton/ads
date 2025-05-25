from playwright.sync_api import sync_playwright
import time
import os
import re
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import io
from googleapiclient.http import MediaIoBaseDownload
from twocaptcha import TwoCaptcha
import subprocess
import requests
import sys
import tarfile
import urllib.request

# Import configuration
try:
    from config import CAPTCHA_API_KEY, BROWSER_HEADLESS, BROWSER_SLOW_MO, STEP_DELAY, RECAPTCHA_WAIT, FORM_LOAD_WAIT, GOOGLE_DRIVE_PARENT_FOLDER, ORBITA_LOGIN_EMAIL, ORBITA_LOGIN_PASSWORD
    print("✅ Configuration loaded from config.py")
except ImportError:
    # Fallback configuration if config.py doesn't exist
    CAPTCHA_API_KEY = "YOUR_2CAPTCHA_API_KEY"
    ORBITA_LOGIN_EMAIL = "your_email@example.com"
    ORBITA_LOGIN_PASSWORD = "your_password"
    BROWSER_HEADLESS = False
    BROWSER_SLOW_MO = 2000
    STEP_DELAY = 2
    RECAPTCHA_WAIT = 3
    FORM_LOAD_WAIT = 3
    GOOGLE_DRIVE_PARENT_FOLDER = "ad"
    print("⚠️ config.py not found - using default configuration")

# Import Tor settings
try:
    from config import USE_TOR_IP_ROTATION, TOR_IP_CHANGE_INTERVAL, TOR_STARTUP_DELAY, TOR_IP_CHANGE_DELAY
except ImportError:
    # Fallback Tor configuration
    USE_TOR_IP_ROTATION = True
    TOR_IP_CHANGE_INTERVAL = 3
    TOR_STARTUP_DELAY = 5
    TOR_IP_CHANGE_DELAY = 3

# Import enhanced security settings
try:
    from config import LOGOUT_BETWEEN_ADS, WAIT_AFTER_LOGOUT, CHANGE_IP_AFTER_LOGOUT
except ImportError:
    # Fallback security configuration
    LOGOUT_BETWEEN_ADS = True
    WAIT_AFTER_LOGOUT = 180
    CHANGE_IP_AFTER_LOGOUT = True

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Log file to track processed ads
LOG_FILE = "processed_ads.log"

class TorIPChanger:
    """Tor IP changing functionality integrated for ad posting automation"""
    
    def __init__(self):
        self.tor_process = None
        self.tor_path = None
        self.is_initialized = False
        self.proxy_config = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        
    def initialize_tor(self):
        """Initialize Tor based on operating system"""
        try:
            print("🔧 Initializing Tor IP changer...")
            
            if os.name == 'posix':  # Linux/Unix
                return self._initialize_tor_linux()
            elif os.name == 'nt':   # Windows
                return self._initialize_tor_windows()
            else:
                print("❌ Unsupported operating system")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing Tor: {e}")
            return False
    
    def _initialize_tor_linux(self):
        """Initialize Tor on Linux/Unix systems"""
        try:
            # Check if running as root (required for Linux)
            if os.geteuid() != 0:
                print("⚠️ Warning: Tor operations may require root privileges on Linux")
            
            # Check if Tor is installed
            if subprocess.run(['which', 'tor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
                print("🔄 Tor not found. Installing...")
                if os.system("sudo apt install tor -y > /dev/null 2>&1") != 0:
                    print("❌ Failed to install Tor. Please install manually: sudo apt install tor")
                    return False
                print("✅ Tor installed successfully")
            else:
                print("✅ Tor is already installed")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Tor on Linux: {e}")
            return False
    
    def _initialize_tor_windows(self):
        """Initialize Tor on Windows systems"""
        try:
            # Read tor path from config file
            tor_path_file = "tor_path.txt"
            if not os.path.exists(tor_path_file):
                # Create default tor_path.txt
                with open(tor_path_file, "w") as f:
                    f.write("C:\\")
            
            with open(tor_path_file, "r") as f:
                extract_path = f.read().strip()
            
            self.tor_path = f"{extract_path}\\Tor Expert Bundle\\tor\\tor.exe"
            
            if not os.path.exists(self.tor_path):
                print("🔄 Tor not found. Downloading and installing...")
                if not self._download_tor_windows(extract_path):
                    return False
            else:
                print("✅ Tor is already installed")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Tor on Windows: {e}")
            return False
    
    def _download_tor_windows(self, extract_path):
        """Download and extract Tor for Windows"""
        try:
            tor_url = "https://archive.torproject.org/tor-package-archive/torbrowser/14.0.7/tor-expert-bundle-windows-x86_64-14.0.7.tar.gz"
            filename = "tor.tar.gz"
            
            print(f"📥 Downloading Tor from {tor_url}")
            urllib.request.urlretrieve(tor_url, filename)
            print("✅ Download complete")
            
            print(f"📂 Extracting to {extract_path}\\Tor Expert Bundle")
            with tarfile.open(filename, "r:gz") as tar:
                tar.extractall(f"{extract_path}\\Tor Expert Bundle", filter='fully_trusted')
            
            os.remove(filename)
            print("✅ Tor extracted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading Tor: {e}")
            return False
    
    def start_tor(self):
        """Start Tor service"""
        try:
            if not self.is_initialized:
                print("❌ Tor not initialized. Call initialize_tor() first")
                return False
            
            print("🔄 Starting Tor service...")
            
            if os.name == 'posix':  # Linux/Unix
                # Check if already running
                result = subprocess.run(["sudo", "service", "tor", "status"], capture_output=True, text=True)
                if "Active: active" in result.stdout:
                    print("✅ Tor is already running")
                else:
                    subprocess.run("sudo service tor start", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(3)
                    print("✅ Tor service started")
                    
            elif os.name == 'nt':   # Windows
                # Check if already running
                result = subprocess.run(["tasklist"], capture_output=True, text=True)
                if "tor.exe" in result.stdout:
                    print("✅ Tor is already running")
                else:
                    self.tor_process = subprocess.Popen([self.tor_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print("✅ Tor started")
            
            # Wait longer for Tor to establish circuits
            print("⏳ Waiting for Tor to establish circuits...")
            time.sleep(10)  # Increased from 3 to 10 seconds
            
            # Try to verify connection multiple times
            print("🔍 Verifying Tor connection...")
            for attempt in range(3):
                if self.get_current_ip(max_retries=2, retry_delay=3):
                    print("✅ Tor connection verified and working")
                    return True
                if attempt < 2:
                    print(f"⏳ Connection attempt {attempt + 1} failed, waiting 5 more seconds...")
                    time.sleep(5)
            
            print("⚠️ Tor started but connection verification failed")
            return True  # Return True anyway, verification might work later
            
        except Exception as e:
            print(f"❌ Error starting Tor: {e}")
            return False
    
    def change_ip(self):
        """Change IP by restarting Tor"""
        try:
            if not self.is_initialized:
                print("❌ Tor not initialized")
                return False
            
            print("🔄 Changing IP address...")
            
            if os.name == 'posix':  # Linux/Unix
                subprocess.run("sudo service tor reload", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            elif os.name == 'nt':   # Windows
                # Kill existing tor process
                subprocess.run(['taskkill', '/F', '/IM', 'tor.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)  # Wait a bit longer
                # Start new tor process
                self.tor_process = subprocess.Popen([self.tor_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
            # Wait for new circuits to establish
            print("⏳ Waiting for new circuits to establish...")
            time.sleep(8)  # Increased wait time
            
            # Verify IP change with multiple attempts
            print("🔍 Verifying IP change...")
            for attempt in range(3):
                new_ip = self.get_current_ip(max_retries=2, retry_delay=3)
                if new_ip:
                    print(f"✅ IP successfully changed to: {new_ip}")
                    return True
                if attempt < 2:
                    print(f"⏳ IP verification attempt {attempt + 1} failed, waiting 5 more seconds...")
                    time.sleep(5)
            
            print("⚠️ IP change completed but verification failed")
            return True  # Proceed anyway
                
        except Exception as e:
            print(f"❌ Error changing IP: {e}")
            return False
    
    def get_current_ip(self, max_retries=3, retry_delay=5):
        """Get current IP address through Tor with retry logic"""
        # List of IP checking services to try
        ip_services = [
            "https://httpbin.org/ip",
            "https://icanhazip.com",
            "https://api.ipify.org?format=json",
            "https://ipinfo.io/json"
        ]
        
        for attempt in range(max_retries):
            for service_url in ip_services:
                try:
                    print(f"🔍 Checking IP address (attempt {attempt + 1}/{max_retries}) via {service_url}...")
                    
                    response = requests.get(service_url, proxies=self.proxy_config, timeout=15)
                    
                    # Parse response based on service
                    if "httpbin.org" in service_url:
                        ip = response.json().get('origin', 'Unknown')
                    elif "icanhazip.com" in service_url:
                        ip = response.text.strip()
                    elif "ipify.org" in service_url:
                        ip = response.json().get('ip', 'Unknown')
                    elif "ipinfo.io" in service_url:
                        ip = response.json().get('ip', 'Unknown')
                    else:
                        ip = response.text.strip()
                    
                    if ip and ip != 'Unknown':
                        print(f"✅ IP verified: {ip}")
                        return ip
                        
                except requests.exceptions.ConnectTimeout:
                    print(f"⏳ Connection timeout to {service_url}")
                    continue
                except requests.exceptions.ProxyError as e:
                    print(f"🔌 Proxy error with {service_url}: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️ Error with {service_url}: {e}")
                    continue
            
            # If all services failed for this attempt, wait before retrying
            if attempt < max_retries - 1:
                print(f"⏳ All services failed on attempt {attempt + 1}, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        print("❌ Failed to verify IP after all attempts with all services")
        return None
    
    def stop_tor(self):
        """Stop Tor service"""
        try:
            print("🛑 Stopping Tor service...")
            
            if os.name == 'posix':  # Linux/Unix
                subprocess.run("sudo service tor stop", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            elif os.name == 'nt' and self.tor_process:  # Windows
                self.tor_process.kill()
                self.tor_process = None
            
            print("✅ Tor stopped")
            
        except Exception as e:
            print(f"⚠️ Error stopping Tor: {e}")
    
    def configure_browser_proxy(self, context):
        """Configure Playwright browser context to use Tor proxy"""
        try:
            # Set proxy for the browser context
            proxy_config = {
                'server': 'socks5://127.0.0.1:9050'
            }
            print("🌐 Configuring browser to use Tor proxy")
            return proxy_config
        except Exception as e:
            print(f"❌ Error configuring browser proxy: {e}")
            return None

class AdLogger:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        self.processed_ads = self.load_processed_ads()
    
    def load_processed_ads(self):
        """Load list of already processed ads from log file"""
        processed = set()
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            processed.add(line)
                print(f"📋 Loaded {len(processed)} processed ads from log")
            except Exception as e:
                print(f"⚠️ Error loading log file: {e}")
        else:
            print("📋 No previous log file found - starting fresh")
        return processed
    
    def is_processed(self, ad_path):
        """Check if ad has already been processed"""
        return ad_path in self.processed_ads
    
    def mark_as_processed(self, ad_path):
        """Mark ad as processed and write to log file"""
        if ad_path not in self.processed_ads:
            self.processed_ads.add(ad_path)
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{ad_path} # Processed on {timestamp}\n")
                print(f"✅ Logged as processed: {ad_path}")
            except Exception as e:
                print(f"❌ Error writing to log: {e}")
    
    def get_stats(self):
        """Get statistics about processed ads"""
        return {
            'total_processed': len(self.processed_ads),
            'log_file': self.log_file
        }

class GoogleDriveClient:
    def __init__(self):
        self.service = None
        self.setup_drive_api()
    
    def setup_drive_api(self):
        """Setup Google Drive API authentication"""
        creds = None
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("❌ Error: credentials.json not found!")
                    print("Please download OAuth2 credentials from Google Cloud Console")
                    print("and save as 'credentials.json' in this directory")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Google Drive API connected successfully!")

    def find_datetime_folders(self, parent_folder_name="ad"):
        """Find folders with datetime format ad/YYYYMMDD/HHMM"""
        try:
            # Search for the parent folder 'ad'
            parent_query = f"name='{parent_folder_name}' and mimeType='application/vnd.google-apps.folder'"
            parent_results = self.service.files().list(q=parent_query).execute()
            parent_folders = parent_results.get('files', [])
            
            if not parent_folders:
                print(f"❌ Parent folder '{parent_folder_name}' not found")
                print(f"📁 Please create a folder named '{parent_folder_name}' in your Google Drive root")
                return []
            
            parent_folder_id = parent_folders[0]['id']
            print(f"✅ Found parent folder: {parent_folder_name}")
            
            # Get all date folders in 'ad' directory (YYYYMMDD format)
            query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query).execute()
            date_folders = results.get('files', [])
            
            # Filter folders that match datetime pattern and get time subfolders
            datetime_folders = []
            date_pattern = re.compile(r'^\d{8}$')  # YYYYMMDD format
            
            for date_folder in date_folders:
                if date_pattern.match(date_folder['name']):
                    # Get time subfolders (HHMM format)
                    time_query = f"'{date_folder['id']}' in parents and mimeType='application/vnd.google-apps.folder'"
                    time_results = self.service.files().list(q=time_query).execute()
                    time_folders = time_results.get('files', [])
                    
                    for time_folder in time_folders:
                        if re.match(r'^\d{4}$', time_folder['name']):  # HHMM format
                            full_path = f"{parent_folder_name}/{date_folder['name']}/{time_folder['name']}"
                            datetime_folders.append({
                                'name': full_path,
                                'id': time_folder['id'],
                                'date': date_folder['name'],
                                'time': time_folder['name'],
                                'path': full_path
                            })
            
            print(f"✅ Found {len(datetime_folders)} datetime folders in '{parent_folder_name}'")
            return sorted(datetime_folders, key=lambda x: x['name'])
            
        except Exception as e:
            print(f"❌ Error searching for folders: {e}")
            return []

    def get_folder_contents(self, folder_id):
        """Get contents of a specific folder"""
        try:
            query = f"'{folder_id}' in parents"
            results = self.service.files().list(q=query).execute()
            files = results.get('files', [])
            
            ad_data = {
                'phone_file': None,
                'ad_text': '',
                'images': [],
                'phone_number': '',
                'apartment_details': {}
            }
            
            for file in files:
                file_name = file['name'].lower()
                
                # Find phone number file (.txt with number in name)
                if file_name.endswith('.txt') and re.search(r'\d+', file['name']):
                    ad_data['phone_file'] = file
                    # Extract phone number from filename
                    phone_match = re.search(r'(\d+)', file['name'])
                    if phone_match:
                        ad_data['phone_number'] = phone_match.group(1)
                    
                    # Download and read ad text
                    ad_data['ad_text'] = self.download_text_file(file['id'])
                
                # Find params.txt file for apartment details
                elif file_name == 'params.txt':
                    params_content = self.download_text_file(file['id'])
                    ad_data['apartment_details'] = self.parse_apartment_details(params_content)
                
                # Find image files
                elif any(file_name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    ad_data['images'].append(file)
            
            return ad_data
            
        except Exception as e:
            print(f"❌ Error getting folder contents: {e}")
            return None

    def parse_apartment_details(self, params_content):
        """Parse apartment details from params.txt content based on line positions"""
        details = {}
        try:
            lines = params_content.strip().split('\n')
            
            # Parse according to specified line positions:
            # Line 2 - address
            if len(lines) > 1:
                details['address'] = lines[1].strip()
                
            # Line 4 - rooms
            if len(lines) > 3:
                details['rooms'] = lines[3].strip()
                
            # Line 6 - floor
            if len(lines) > 5:
                details['floor'] = lines[5].strip()
                
            # Line 8 - furniture
            if len(lines) > 7:
                details['furniture'] = lines[7].strip()
                
            # Line 10 - price
            if len(lines) > 9:
                details['price'] = lines[9].strip()
                
            print(f"✅ Parsed apartment details: {details}")
            return details
            
        except Exception as e:
            print(f"❌ Error parsing apartment details: {e}")
            return details

    def download_text_file(self, file_id):
        """Download and return text content of a file"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            content = file_io.getvalue().decode('utf-8')
            return content
            
        except Exception as e:
            print(f"❌ Error downloading text file: {e}")
            return ""

    def download_image_file(self, file_id, local_path):
        """Download an image file to local storage"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            with open(local_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            return True
            
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return False

def dismiss_notifications(page):
    """Dismiss any notification popups that appear"""
    try:
        # Wait a moment for popups to appear
        time.sleep(2)
        
        # Try to dismiss various types of popups/notifications
        dismiss_selectors = [
            # Notification permission popups
            'button:text("Cancel")',
            'button:text("Block")', 
            'button:text("Not now")',
            'button:text("No thanks")',
            'button:text("Deny")',
            'button:text("Don\'t allow")',
            
            # General close buttons
            '[data-testid="dismiss"]',
            '.notification-dismiss',
            '[aria-label="Close"]',
            'button[aria-label="Cancel"]',
            '.close-button',
            '.modal-close',
            
            # Cookie/GDPR popups
            'button:text("Accept")',
            'button:text("OK")',
            '.cookie-accept',
            '.gdpr-accept'
        ]
        
        dismissed_count = 0
        for selector in dismiss_selectors:
            try:
                elements = page.locator(selector)
                if elements.count() > 0:
                    # Try to click each matching element
                    for i in range(min(elements.count(), 3)):  # Limit to 3 elements
                        try:
                            elements.nth(i).click(timeout=1000)
                            dismissed_count += 1
                            time.sleep(0.5)
                        except:
                            continue
            except:
                continue
        
        if dismissed_count > 0:
            print(f"✅ Dismissed {dismissed_count} popup(s)")
        
        # Try pressing Escape key to dismiss any remaining modals
        try:
            page.keyboard.press('Escape')
            time.sleep(1)
        except:
            pass
            
    except Exception as e:
        print(f"⚠️ Could not dismiss popups: {e}")
        # Continue anyway - this shouldn't stop the form filling

def detect_recaptcha(page):
    """Detect if reCAPTCHA is present on the page"""
    try:
        # Check for various reCAPTCHA selectors
        recaptcha_selectors = [
            '#rc-anchor-container',  # Main reCAPTCHA container
            '.g-recaptcha',          # Standard reCAPTCHA class
            '.recaptcha-checkbox',   # reCAPTCHA checkbox
            'iframe[src*="recaptcha"]', # reCAPTCHA iframe
            '[data-sitekey]'         # Element with reCAPTCHA site key
        ]
        
        for selector in recaptcha_selectors:
            if page.locator(selector).count() > 0:
                print(f"🤖 reCAPTCHA detected using selector: {selector}")
                return True
        
        return False
        
    except Exception as e:
        print(f"⚠️ Error detecting reCAPTCHA: {e}")
        return False

def get_recaptcha_sitekey(page):
    """Extract reCAPTCHA site key from the page"""
    try:
        # Try different methods to get the site key
        sitekey_selectors = [
            '[data-sitekey]',
            '.g-recaptcha[data-sitekey]',
            'div[data-sitekey]'
        ]
        
        for selector in sitekey_selectors:
            element = page.locator(selector).first
            if element.count() > 0:
                sitekey = element.get_attribute('data-sitekey')
                if sitekey:
                    print(f"🔑 Found reCAPTCHA site key: {sitekey[:20]}...")
                    return sitekey
        
        # If no sitekey found, try to extract from iframe src
        iframe_locator = page.locator('iframe[src*="recaptcha"]').first
        if iframe_locator.count() > 0:
            iframe_src = iframe_locator.get_attribute('src')
            if iframe_src and 'k=' in iframe_src:
                sitekey = iframe_src.split('k=')[1].split('&')[0]
                print(f"🔑 Extracted reCAPTCHA site key from iframe: {sitekey[:20]}...")
                return sitekey
        
        print("⚠️ Could not find reCAPTCHA site key")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting reCAPTCHA site key: {e}")
        return None

def solve_recaptcha_simple(page, api_key):
    """Solve reCAPTCHA using simplified approach from working test"""
    try:
        # Find captcha site key
        site_key = None
        try:
            site_key = page.get_attribute('[data-sitekey]', 'data-sitekey')
        except:
            pass
        
        if not site_key:
            print("❌ No reCAPTCHA site key found")
            return False
        
        print(f"🔑 Found site key: {site_key[:20]}...")
        
        # Solve with 2captcha
        solver = TwoCaptcha(api_key)
        result = solver.recaptcha(sitekey=site_key, url=page.url, version='v2')
        
        if result and 'code' in result:
            print("🔧 Injecting captcha solution...")
            
            # Inject solution with simpler method
            inject_script = f"""
                () => {{
                    try {{
                        // Set the response in the hidden textarea
                        const responseTextarea = document.getElementById('g-recaptcha-response');
                        if (responseTextarea) {{
                            responseTextarea.value = '{result['code']}';
                            responseTextarea.style.display = 'block';
                        }}
                        
                        // Also set in any other captcha response fields
                        const allCaptchaInputs = document.querySelectorAll('textarea[name="g-recaptcha-response"]');
                        allCaptchaInputs.forEach(input => {{
                            input.value = '{result['code']}';
                        }});
                        
                        return true;
                    }} catch(error) {{
                        console.error('Captcha injection error:', error);
                        return false;
                    }}
                }}
            """
            
            # Execute the injection script
            success = page.evaluate(inject_script)
            
            if success:
                print("✅ reCAPTCHA solution injected successfully")
                
                # Wait a bit for the captcha to be processed
                time.sleep(2)
                
                # Verify the solution was accepted
                response_value = page.evaluate("""
                    () => {
                        const textarea = document.getElementById('g-recaptcha-response');
                        return textarea ? textarea.value : '';
                    }
                """)
                
                if response_value:
                    print(f"✅ Captcha response verified: {response_value[:50]}...")
                    return True
                else:
                    print("❌ Captcha response not found after injection")
                    return False
            else:
                print("❌ Failed to inject captcha solution")
                return False
        else:
            print("❌ Failed to get captcha solution from 2captcha")
            return False
            
    except Exception as e:
        print(f"❌ Captcha solving error: {e}")
        return False

def solve_recaptcha(page, sitekey, api_key):
    """Solve reCAPTCHA using 2captcha service"""
    try:
        if not api_key or api_key == "YOUR_2CAPTCHA_API_KEY":
            print("❌ Please set your 2captcha API key in CAPTCHA_API_KEY variable")
            return False
        
        print("🔄 Solving reCAPTCHA using 2captcha service...")
        
        # Initialize 2captcha solver
        solver = TwoCaptcha(api_key)
        
        # Get current page URL
        current_url = page.url
        print(f"🌐 Page URL: {current_url}")
        print(f"🔑 Site key: {sitekey[:20]}...")
        
        # Submit reCAPTCHA to 2captcha
        print("📤 Submitting reCAPTCHA to 2captcha...")
        result = solver.recaptcha(
            sitekey=sitekey,
            url=current_url,
            version='v2'
        )
        
        if result and 'code' in result:
            captcha_response = result['code']
            print(f"✅ reCAPTCHA solved! Token received: {captcha_response[:50]}...")
            
            # Inject the reCAPTCHA response into the page
            inject_script = f"""
            // Function to set reCAPTCHA response
            function setRecaptchaResponse(token) {{
                // Method 1: Set in standard response textarea
                const responseElement = document.getElementById('g-recaptcha-response');
                if (responseElement) {{
                    responseElement.innerHTML = token;
                    responseElement.value = token;
                }}
                
                // Method 2: Set in any hidden recaptcha response fields
                const hiddenElements = document.querySelectorAll('[name="g-recaptcha-response"]');
                hiddenElements.forEach(el => {{
                    el.value = token;
                }});
                
                // Method 3: Trigger callback if exists
                if (window.grecaptcha && window.grecaptcha.getResponse) {{
                    // Try to find the widget ID and set response
                    for (let i = 0; i < 10; i++) {{
                        try {{
                            window.grecaptcha.reset(i);
                            // Set the response for this widget
                        }} catch(e) {{
                            // Widget doesn't exist, continue
                        }}
                    }}
                }}
                
                // Method 4: Dispatch events to notify the page
                const event = new Event('change', {{ bubbles: true }});
                if (responseElement) {{
                    responseElement.dispatchEvent(event);
                }}
                
                console.log('reCAPTCHA response set:', token.substring(0, 50) + '...');
                return true;
            }}
            
            setRecaptchaResponse('{captcha_response}');
            """
            
            # Execute the injection script
            page.evaluate(inject_script)
            print("💉 reCAPTCHA response injected into page")
            
            # Wait a moment for the page to process the response
            time.sleep(2)
            
            # Check if reCAPTCHA is now solved
            is_solved = page.evaluate("""
                () => {
                    const responseElement = document.getElementById('g-recaptcha-response');
                    return responseElement && responseElement.value && responseElement.value.length > 100;
                }
            """)
            
            if is_solved:
                print("✅ reCAPTCHA successfully solved and verified!")
                return True
            else:
                print("⚠️ reCAPTCHA response injected but verification unclear")
                return True  # Proceed anyway
                
        else:
            print("❌ Failed to solve reCAPTCHA - no valid response received")
            return False
            
    except Exception as e:
        print(f"❌ Error solving reCAPTCHA: {e}")
        return False

def handle_recaptcha(page):
    """Main function to handle reCAPTCHA detection and solving"""
    try:
        print("🔍 Checking for reCAPTCHA...")
        
        # Wait a moment for reCAPTCHA to load
        time.sleep(3)
        
        if detect_recaptcha(page):
            print("🤖 reCAPTCHA detected! Attempting to solve...")
            
            # Solve the reCAPTCHA
            success = solve_recaptcha_simple(page, CAPTCHA_API_KEY)
            
            if success:
                print("✅ reCAPTCHA handling completed successfully!")
                return True
            else:
                print("❌ Failed to solve reCAPTCHA")
                return False
        else:
            print("✅ No reCAPTCHA detected - proceeding normally")
            return True
            
    except Exception as e:
        print(f"❌ Error handling reCAPTCHA: {e}")
        return False

def get_phone_prefix(phone_number):
    """Extract first 2 digits for phone prefix selection"""
    if len(phone_number) >= 2:
        return phone_number[:2]
    return "05"  # Default fallback

def fill_single_ad(page, ad_data):
    """Fill form for a single ad with new workflow"""
    try:
        print(f"\n📝 Filling form for phone: {ad_data['phone_number']}")
        
        # STEP 1: Board selection dropdown - 'Квартиры - продам' (value="45")
        print("📋 Step 1: Selecting board: Квартиры - продам")
        board_selectors = [
            'select[name="board"]',
            'select#board',
            'select.board-select',
            'select:has(option[value="45"])'
        ]
        
        for selector in board_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.select_option(selector, value='45')  # Use value instead of label
                    print("✅ Board selected successfully")
                    break
            except:
                continue
        else:
            print("⚠️ Board selector not found, trying alternative method")
            try:
                page.click('text=Выберите доску')
                time.sleep(1)
                page.click('option[value="45"]')
                print("✅ Board selected via option click")
            except Exception as e:
                print(f"❌ Could not select board: {e}")

        # STEP 2: Wait for form to change after board selection
        print("⏳ Step 2: Waiting for form to update...")
        time.sleep(3)  # Wait for form to reload/update

        # STEP 3: City selection - 'Ришон ле Цион'
        print("🏙️ Step 3: Selecting city: Ришон ле Цион")
        city_selectors = [
            'select[name="city"]',
            'select#city', 
            'select.city-select',
            'select:has(option:text("Ришон"))'
        ]
        
        for selector in city_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.select_option(selector, label='Ришон ле Цион')
                    print("✅ City selected successfully")
                    break
            except:
                continue
        else:
            print("⚠️ City selector not found, trying alternative method")
            try:
                page.click('text=Выберите город')
                time.sleep(1)
                page.click('text=Ришон ле Цион')
                print("✅ City selected via text click")
            except Exception as e:
                print(f"❌ Could not select city: {e}")

        time.sleep(2)

        # STEP 4: Fill apartment details from params.txt
        print("🏠 Step 4: Filling apartment details")
        apartment_details = ad_data.get('apartment_details', {})
        
        # Address - input into input[name="address"]
        if 'address' in apartment_details:
            print(f"📍 Filling address: {apartment_details['address']}")
            try:
                if page.locator('input[name="address"]').count() > 0:
                    page.fill('input[name="address"]', apartment_details['address'])
                    print("✅ Address filled successfully")
                else:
                    print("⚠️ Address input field not found")
            except Exception as e:
                print(f"❌ Error filling address: {e}")

        # Rooms - select[name="room"] with specific value mapping
        if 'rooms' in apartment_details:
            print(f"🚪 Filling rooms: {apartment_details['rooms']}")
            try:
                rooms_value = apartment_details['rooms']
                # Map room values to option values
                room_mapping = {
                    "1": "77", "1.5": "78", "2": "79", "2.5": "80",
                    "3": "81", "3.5": "82", "4": "83", "4.5": "84",
                    "5": "85", "5.5": "86", "6+": "87"
                }
                
                option_value = room_mapping.get(rooms_value, "0")  # Default to "Не указано"
                
                if page.locator('select[name="room"]').count() > 0:
                    page.select_option('select[name="room"]', value=option_value)
                    print(f"✅ Rooms filled successfully: {rooms_value} (option value: {option_value})")
                else:
                    print("⚠️ Rooms select field not found")
            except Exception as e:
                print(f"❌ Error filling rooms: {e}")

        # Floor - select[name="floor"] with specific value mapping
        if 'floor' in apartment_details:
            print(f"🏢 Filling floor: {apartment_details['floor']}")
            try:
                floor_value = apartment_details['floor']
                # Map floor values to option values
                floor_mapping = {
                    "0": "57", "1": "58", "2": "59", "3": "60", "4": "61",
                    "5": "62", "6": "63", "7": "64", "8": "65", "9": "66",
                    "10+": "67"
                }
                
                option_value = floor_mapping.get(floor_value, "0")  # Default to "Не указано"
                
                if page.locator('select[name="floor"]').count() > 0:
                    page.select_option('select[name="floor"]', value=option_value)
                    print(f"✅ Floor filled successfully: {floor_value} (option value: {option_value})")
                else:
                    print("⚠️ Floor select field not found")
            except Exception as e:
                print(f"❌ Error filling floor: {e}")

        # Furniture - select[name="furniture"] with specific value mapping
        if 'furniture' in apartment_details:
            print(f"🛋️ Filling furniture: {apartment_details['furniture']}")
            try:
                furniture_value = apartment_details['furniture'].lower()
                # Map furniture values to option values
                furniture_mapping = {
                    "да": "26", "нет": "27", "частично": "28"
                }
                
                option_value = furniture_mapping.get(furniture_value, "0")  # Default to "Не указано"
                
                if page.locator('select[name="furniture"]').count() > 0:
                    page.select_option('select[name="furniture"]', value=option_value)
                    print(f"✅ Furniture filled successfully: {furniture_value} (option value: {option_value})")
                else:
                    print("⚠️ Furniture select field not found")
            except Exception as e:
                print(f"❌ Error filling furniture: {e}")

        # Price - input into input[name="cost"]
        if 'price' in apartment_details:
            print(f"💰 Filling price: {apartment_details['price']}")
            try:
                if page.locator('input[name="cost"]').count() > 0:
                    page.fill('input[name="cost"]', apartment_details['price'])
                    print("✅ Price filled successfully")
                else:
                    print("⚠️ Price input field not found")
            except Exception as e:
                print(f"❌ Error filling price: {e}")

        time.sleep(2)

        # STEP 5: Ad text (Текст объявления) - correct field name
        print("📝 Step 5: Filling ad text")
        ad_text_selectors = [
            'textarea[name="info"]',  # Correct field name from HTML
            'textarea#info',
            'textarea.form-control:has([name="info"])'
        ]
        
        for selector in ad_text_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, ad_data['ad_text'])
                    print("✅ Ad text filled successfully")
                    break
            except:
                continue
        else:
            print(f"⚠️ Ad text field not found. Text to fill: {ad_data['ad_text'][:50]}...")

        time.sleep(2)

        # STEP 6: Image uploads (5 separate inputs targeted by row titles)
        print(f"🖼️ Step 6: Uploading {len(ad_data['images'])} images to specific photo inputs")
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download images temporarily
        downloaded_images = []
        for i, img in enumerate(ad_data['images'][:5]):  # Limit to 5 images
            temp_path = os.path.join(temp_dir, f"img_{i}_{img['name']}")
            if drive_client.download_image_file(img['id'], temp_path):
                downloaded_images.append(temp_path)
                print(f"✅ Downloaded: {img['name']}")

        # Upload to specific file inputs by targeting rows with titles
        for i in range(1, 6):  # Фото 1 through Фото 5
            if i-1 < len(downloaded_images):
                try:
                    # Target file input by finding the row with the specific photo title
                    photo_title = f"Фото {i}"
                    upload_selectors = [
                        # Target input near the specific photo title
                        f'input[type="file"][name="photo[]"]:near(:text("{photo_title}"))',
                        # Target by row structure - find div containing the title, then the file input
                        f'div:has(:text("{photo_title}")) input[type="file"][name="photo[]"]',
                        # Alternative selectors for the photo inputs
                        f'input[name="photo[]"]:nth-of-type({i})',
                        # Generic photo array selector with index
                        f'input[name="photo[{i-1}]"]'
                    ]
                    
                    upload_success = False
                    for selector in upload_selectors:
                        try:
                            if page.locator(selector).count() > 0:
                                page.set_input_files(selector, downloaded_images[i-1])
                                print(f"✅ Uploaded image {i} ({photo_title}): {os.path.basename(downloaded_images[i-1])}")
                                upload_success = True
                                break
                        except Exception as sel_e:
                            continue
                    
                    if not upload_success:
                        # Final fallback - try to find the input by position in all file inputs
                        try:
                            all_file_inputs = page.locator('input[type="file"][name="photo[]"]')
                            if all_file_inputs.count() >= i:
                                all_file_inputs.nth(i-1).set_input_files(downloaded_images[i-1])
                                print(f"✅ Uploaded image {i} via fallback method: {os.path.basename(downloaded_images[i-1])}")
                            else:
                                print(f"⚠️ File upload field {i} not found (not enough photo inputs)")
                        except Exception as fallback_e:
                            print(f"❌ Failed to upload image {i} even with fallback: {fallback_e}")
                            
                except Exception as e:
                    print(f"❌ Failed to upload image {i}: {e}")

        time.sleep(2)

        # STEP 7: Phone number
        print(f"📱 Step 7: Filling phone number: {ad_data['phone_number']}")
        
        # Phone prefix (first 2 digits)
        phone_prefix = get_phone_prefix(ad_data['phone_number'])
        prefix_selectors = [
            'select[name="phone_prefix"]',
            'select#phone_prefix',
            'select.phone-prefix'
        ]
        
        for selector in prefix_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.select_option(selector, value=phone_prefix)
                    print(f"✅ Phone prefix selected: {phone_prefix}")
                    break
            except:
                continue

        # Phone number field - correct field name
        phone_selectors = [
            'input[name="phonenum"]',  # Correct field name from HTML
            'input#phonenum',
            'input.form-control:has([name="phonenum"])'
        ]
        
        for selector in phone_selectors:
            try:
                if page.locator(selector).count() > 0:
                    # Use the full phone number without splitting prefix
                    page.fill(selector, ad_data['phone_number'])
                    print("✅ Phone number filled successfully")
                    break
            except:
                continue

        time.sleep(1)

        # STEP 8: Agreement checkbox - correct field name
        print("✅ Step 8: Checking agreement checkbox")
        agreement_selectors = [
            'input[name="terms"]',  # Correct field name from HTML
            'input#terms',
            'input[type="checkbox"][name="terms"]'
        ]
        
        for selector in agreement_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.check(selector)
                    print("✅ Agreement checkbox checked")
                    break
            except:
                continue
        else:
            print("⚠️ Agreement checkbox not found")

        time.sleep(1)

        # STEP 9: Handle reCAPTCHA if present (moved to just before submission)
        print("🤖 Step 9: Checking and handling reCAPTCHA before submission")
        recaptcha_success = handle_recaptcha(page)
        if not recaptcha_success:
            print("❌ reCAPTCHA handling failed - this may prevent form submission")
        
        time.sleep(1)

        # STEP 10: Submit button (NOW ENABLED - authentication working!)
        print("🚀 Step 10: Submitting form...")
        
        submit_selectors = [
            '#submit_but',  # From our testing, this is the correct ID
            'button[type="submit"]',
            'input[type="submit"]',
            'button:text("Добавить объявление")',
            '.submit-btn'
        ]
        
        submitted = False
        for selector in submit_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.click(selector)
                    print("✅ Form submitted successfully!")
                    time.sleep(5)  # Wait for submission response
                    submitted = True
                    break
            except:
                continue
        
        if not submitted:
            print("❌ Submit button not found")
            return False
        
        # Check if submission was successful
        current_url = page.url
        if "addsuccess=1" in current_url:
            print("🎉 SUCCESS! Ad posted successfully!")
            return True
        elif "passport.orbita.co.il/site/login" in current_url:
            print("❌ Redirected to login - authentication issue")
            return False
        elif "my/add" in current_url:
            print("⚠️ Still on form page - checking for validation errors...")
            # Check for validation errors
            try:
                error_elements = page.locator('.alert, .error, .help-block, .text-danger').all()
                for element in error_elements:
                    error_text = element.text_content()
                    if error_text and error_text.strip():
                        print(f"❌ Form error: {error_text}")
            except:
                pass
            return False
        else:
            print(f"🤔 Unexpected page after submission: {current_url}")
            return False

        print(f"✅ Completed form processing for phone: {ad_data['phone_number']}")
        return True

    except Exception as e:
        print(f"❌ Error filling form for {ad_data['phone_number']}: {e}")
        return False

def authenticate_orbita(page):
    """
    Authenticate with Orbita.co.il account
    Returns True if login successful, False otherwise
    """
    try:
        print("🔐 Authenticating with Orbita.co.il...")
        
        # Navigate to login page
        page.goto("https://passport.orbita.co.il/site/login")
        page.wait_for_load_state('networkidle')
        
        # Fill login form
        page.fill('#loginform-email', ORBITA_LOGIN_EMAIL)
        time.sleep(1)  # Human-like delay
        page.fill('#loginform-password', ORBITA_LOGIN_PASSWORD)
        time.sleep(1)
        
        print("📧 Credentials filled, submitting login...")
        
        # Submit login form
        page.click('button[name="login-button"]')
        page.wait_for_timeout(3000)
        
        # Check if login was successful
        current_url = page.url
        if "passport.orbita.co.il/site/login" not in current_url:
            print(f"✅ Login successful! Redirected to: {current_url}")
            return True
        else:
            # Check for error messages
            try:
                error_elements = page.locator('.alert, .error, .invalid-feedback').all()
                for element in error_elements:
                    error_text = element.text_content()
                    if error_text and error_text.strip():
                        print(f"❌ Login error: {error_text}")
            except:
                pass
            print("❌ Login failed - still on login page")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def logout_orbita(page):
    """
    Logout from Orbita.co.il account
    Returns True if logout successful, False otherwise
    """
    try:
        print("🚪 Logging out from Orbita.co.il...")
        
        # Navigate to logout page
        page.goto("https://doska.orbita.co.il/app/site/logout")
        page.wait_for_load_state('networkidle')
        time.sleep(2)  # Give time for logout to process
        
        # Verify logout by checking if we're redirected to login page or homepage
        current_url = page.url
        if "logout" in current_url or "login" in current_url or "orbita.co.il" in current_url:
            print("✅ Successfully logged out")
            return True
        else:
            print(f"⚠️ Logout unclear - current URL: {current_url}")
            return True  # Proceed anyway
            
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return False

def main():
    """Main function - PRODUCTION MODE with live website"""
    print("🚀 ORBITA FORM FILLER - PRODUCTION MODE")
    print("=" * 50)
    print("⚠️  WILL SUBMIT TO LIVE WEBSITE!")
    print("📁 Looking for ads in 'ad' folder structure")
    print("=" * 50)

    # Initialize ad logger
    logger = AdLogger()
    stats = logger.get_stats()
    print(f"📊 Previously processed ads: {stats['total_processed']}")

    # Initialize Tor IP changer
    tor_changer = None
    if USE_TOR_IP_ROTATION:
        print("\n🔧 Initializing Tor IP changer...")
        tor_changer = TorIPChanger()
        if tor_changer.initialize_tor():
            if tor_changer.start_tor():
                print(f"🌐 Current IP: {tor_changer.get_current_ip()}")
                time.sleep(TOR_STARTUP_DELAY)
            else:
                print("⚠️ Failed to start Tor, continuing without IP rotation")
                tor_changer = None
        else:
            print("⚠️ Failed to initialize Tor, continuing without IP rotation")
            tor_changer = None
    else:
        print("⚠️ Tor IP rotation disabled in config")

    # Initialize Google Drive client
    global drive_client
    try:
        print("\n🔌 Connecting to Google Drive...")
        drive_client = GoogleDriveClient()
        if not drive_client.service:
            print("❌ Could not connect to Google Drive")
            return
    except Exception as e:
        print(f"❌ Error connecting to Google Drive: {e}")
        return

    # Get ad folders from Google Drive
    try:
        ad_folders = drive_client.find_datetime_folders("ad")  # Use 'ad' folder
        if not ad_folders:
            print("⚠️ No datetime folders found in 'ad' folder")
            print("📁 Please create folders in format: ad/YYYYMMDD/HHMM")
            return
    except Exception as e:
        print(f"❌ Error accessing Google Drive: {e}")
        return

    print(f"\n📊 Found {len(ad_folders)} ad folders to process")

    # Filter out already processed ads
    new_ads = []
    skipped_ads = []
    
    for folder in ad_folders:
        if logger.is_processed(folder['path']):
            skipped_ads.append(folder['path'])
        else:
            new_ads.append(folder)
    
    print(f"✅ New ads to process: {len(new_ads)}")
    print(f"⏭️ Skipped (already processed): {len(skipped_ads)}")
    
    if skipped_ads:
        print("\n📋 Skipped ads:")
        for ad_path in skipped_ads:
            print(f"   ⏭️ {ad_path}")

    if not new_ads:
        print("\n🎉 All ads have been processed already!")
        return

    # Confirm before proceeding
    print(f"\n⚠️ WARNING: About to process {len(new_ads)} ads on LIVE WEBSITE!")
    confirm = input("Type 'YES' to continue: ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return

    with sync_playwright() as p:
        # Prepare browser launch options with anti-detection measures
        browser_args = [
            '--no-blink-features=AutomationControlled',  # Hide automation
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking'
        ]
        
        launch_options = {
            'headless': False,
            'slow_mo': 2000,  # Slower for production
            'args': browser_args
        }
        
        # Add Tor proxy to browser launch if available
        if tor_changer and tor_changer.is_initialized:
            proxy_config = tor_changer.configure_browser_proxy(None)
            if proxy_config:
                launch_options['proxy'] = proxy_config
                print("🌐 Browser will launch with Tor proxy")
        
        # Launch browser with proxy configuration at launch level
        browser = p.chromium.launch(**launch_options)
        
        # Create context with human-like settings
        context_options = {
            'permissions': [],  # No permissions granted initially
            'geolocation': None,
            'ignore_https_errors': True,
            'viewport': {'width': 1366, 'height': 768},  # Common screen resolution
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extra_http_headers': {
                'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
        }
        
        context = browser.new_context(**context_options)
        
        # Explicitly deny notifications
        context.grant_permissions([], origin="https://doska.orbita.co.il")
        
        page = context.new_page()
        
        # Inject stealth scripts to avoid detection
        stealth_script = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });

        // Mock languages and plugins to look more human
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'ru'],
        });

        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // Override the `plugins` property to use a custom getter.
        Object.defineProperty(navigator, 'plugins', {
            get: function() {
                return [
                    {
                        0: {
                            type: "application/x-google-chrome-pdf",
                            suffixes: "pdf",
                            description: "Portable Document Format",
                            enabledPlugin: Plugin,
                        },
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin",
                    },
                ];
            },
        });

        // Overwrite the `chrome` object to prevent detection
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };

        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        
        # Execute stealth script on every page navigation
        page.add_init_script(stealth_script)
        
        # Handle any popup dialogs that appear
        page.on("dialog", lambda dialog: dialog.dismiss())
        
        # Suppress JavaScript errors in console to avoid interference
        page.on("pageerror", lambda error: print(f"🔇 Suppressed JS error: {error}"))
        
        try:
            # First authenticate with Orbita.co.il
            if not authenticate_orbita(page):
                print("❌ Authentication failed - cannot proceed")
                return
            
            # Wait a few seconds after login
            print("⏳ Waiting a few seconds after login...")
            time.sleep(3)
            
            # Navigate to the ad posting page
            page.goto("https://doska.orbita.co.il/my/add/")
            page.wait_for_load_state('networkidle')
            print("✅ Ad posting page loaded successfully")

            # Dismiss notifications with a more gentle approach
            dismiss_notifications(page)

            # Process each new ad folder
            processed_count = 0
            failed_count = 0
            
            for i, folder in enumerate(new_ads, 1):
                print(f"\n📁 Processing folder {i}/{len(new_ads)}: {folder['path']}")
                
                # Get ad data from Google Drive
                ad_data = drive_client.get_folder_contents(folder['id'])
                if not ad_data:
                    print(f"⚠️ No data found in folder {folder['path']}")
                    failed_count += 1
                    continue

                if not ad_data['phone_number']:
                    print(f"⚠️ No phone number found in folder {folder['path']}")
                    failed_count += 1
                    continue

                # Fill the form
                success = fill_single_ad(page, ad_data)
                
                if success:
                    print(f"✅ Successfully processed: {folder['path']}")
                    logger.mark_as_processed(folder['path'])
                    processed_count += 1
                else:
                    print(f"❌ Failed to process: {folder['path']}")
                    failed_count += 1

                # Enhanced security workflow between ads
                if i < len(new_ads):
                    print(f"\n🔄 Starting enhanced security workflow before next ad...")
                    
                    # Step 1: Logout after each ad (if enabled)
                    if LOGOUT_BETWEEN_ADS:
                        logout_success = logout_orbita(page)
                        if not logout_success:
                            print("⚠️ Logout failed, but continuing...")
                    
                    # Step 2: Wait for specified time (default 3 minutes)
                    wait_minutes = WAIT_AFTER_LOGOUT // 60
                    wait_seconds = WAIT_AFTER_LOGOUT % 60
                    print(f"⏳ Waiting for {wait_minutes} minutes and {wait_seconds} seconds...")
                    
                    # Show countdown for better UX
                    for remaining in range(WAIT_AFTER_LOGOUT, 0, -30):
                        mins = remaining // 60
                        secs = remaining % 60
                        print(f"⏰ Time remaining: {mins}m {secs}s...")
                        time.sleep(min(30, remaining))
                    
                    print("✅ Wait period completed")
                    
                    # Step 3: Change IP (if Tor is enabled and configured)
                    if CHANGE_IP_AFTER_LOGOUT and tor_changer and tor_changer.is_initialized:
                        print("🔄 Changing IP address for next ad...")
                        if tor_changer.change_ip():
                            print("✅ IP changed successfully")
                            time.sleep(TOR_IP_CHANGE_DELAY)
                        else:
                            print("⚠️ IP change failed, but continuing...")
                    elif CHANGE_IP_AFTER_LOGOUT and not tor_changer:
                        print("⚠️ IP change requested but Tor not available")
                    
                    # Step 4: Re-authenticate for next ad
                    print("🔐 Re-authenticating for next ad...")
                    if not authenticate_orbita(page):
                        print("❌ Re-authentication failed - stopping processing")
                        break
                    
                    # Step 5: Navigate to ad posting page
                    print("📝 Navigating to ad posting page...")
                    page.goto("https://doska.orbita.co.il/my/add/")
                    page.wait_for_load_state('networkidle')
                    print("✅ Ready for next ad")
                    
                    # Dismiss notifications again
                    dismiss_notifications(page)

        except Exception as e:
            print(f"❌ Error during form filling: {e}")
        finally:
            # Stop Tor if it was started
            if tor_changer:
                tor_changer.stop_tor()
            
            # Show final statistics
            final_stats = logger.get_stats()
            print(f"\n📊 FINAL STATISTICS:")
            print(f"   ✅ Successfully processed: {processed_count}")
            print(f"   ❌ Failed: {failed_count}")
            print(f"   📋 Total processed ads: {final_stats['total_processed']}")
            print(f"   📄 Log file: {final_stats['log_file']}")
            
            print("\n🏁 Production run completed!")
            input("Press Enter to close browser...")
            browser.close()

if __name__ == "__main__":
    main() 