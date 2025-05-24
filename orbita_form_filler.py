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

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Log file to track processed ads
LOG_FILE = "processed_ads.log"

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
            
            # Get the site key
            sitekey = get_recaptcha_sitekey(page)
            if not sitekey:
                print("❌ Could not extract reCAPTCHA site key")
                return False
            
            # Solve the reCAPTCHA
            success = solve_recaptcha(page, sitekey, CAPTCHA_API_KEY)
            
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

        # STEP 8: Email (check if field exists and is required after authentication)
        print("📧 Step 8: Checking email field...")
        email_selectors = [
            'input[name="email"]',
            'input#email',
            'input[type="email"]'
        ]
        
        email_filled = False
        for selector in email_selectors:
            try:
                email_input = page.locator(selector)
                if email_input.count() > 0:
                    # Check if field is visible and editable
                    is_visible = email_input.is_visible()
                    is_enabled = email_input.is_enabled() 
                    current_value = email_input.input_value()
                    
                    print(f"📧 Email field found - Visible: {is_visible}, Enabled: {is_enabled}, Current value: '{current_value}'")
                    
                    if is_visible and is_enabled and not current_value:
                        page.fill(selector, '111@gmail.com')
                        print("✅ Email filled: 111@gmail.com")
                        email_filled = True
                    else:
                        print("ℹ️ Email field not filled (already has value or not editable after login)")
                        email_filled = True
                    break
            except:
                continue
        
        if not email_filled:
            print("ℹ️ No email field found (normal after authentication)")

        time.sleep(1)

        # STEP 9: Handle reCAPTCHA if present
        print("🤖 Step 9: Checking and handling reCAPTCHA")
        recaptcha_success = handle_recaptcha(page)
        if not recaptcha_success:
            print("❌ reCAPTCHA handling failed - this may prevent form submission")
        
        time.sleep(1)

        # STEP 10: Agreement checkbox - correct field name
        print("✅ Step 10: Checking agreement checkbox")
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

        # STEP 11: Submit button (NOW ENABLED - authentication working!)
        print("🚀 Step 11: Submitting form...")
        
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
        # Launch browser with anti-detection measures
        browser = p.chromium.launch(
            headless=False, 
            slow_mo=2000,  # Slower for production
            args=[
                '--no-blink-features=AutomationControlled',  # Hide automation
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-default-apps',
                '--disable-popup-blocking'
            ]
        )
        
        # Create context with human-like settings
        context = browser.new_context(
            permissions=[],  # No permissions granted initially
            geolocation=None,
            ignore_https_errors=True,
            viewport={'width': 1366, 'height': 768},  # Common screen resolution
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
        )
        
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

            # Handle reCAPTCHA
            if handle_recaptcha(page):
                print("✅ reCAPTCHA handling completed successfully!")

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

                # Wait between ads and navigate back to form
                if i < len(new_ads):
                    print(f"\n⏳ Waiting 10 seconds before next ad...")
                    time.sleep(10)
                    # Navigate back to add form for next ad
                    page.goto("https://doska.orbita.co.il/my/add/")
                    page.wait_for_load_state('networkidle')

        except Exception as e:
            print(f"❌ Error during form filling: {e}")
        finally:
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