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
        """Parse apartment details from params.txt content"""
        details = {}
        try:
            lines = params_content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse each line for apartment details
                if line.startswith('Адрес'):
                    details['address'] = line.split('\n', 1)[1].strip() if '\n' in line else line.replace('Адрес', '').strip()
                elif line.startswith('Комнаты'):
                    details['rooms'] = line.replace('Комнаты', '').strip()
                elif line.startswith('Этаж'):
                    details['floor'] = line.replace('Этаж', '').strip()
                elif line.startswith('Мебель'):
                    details['furniture'] = line.replace('Мебель', '').strip()
                elif line.startswith('Цена'):
                    details['price'] = line.replace('Цена', '').strip()
                else:
                    # Handle multi-line address format
                    if 'address' not in details and any(city in line for city in ['Ришон', 'Тель-Авив', 'Иерусалим', 'Хайфа']):
                        details['address'] = line.strip()
            
            print(f"📋 Parsed apartment details: {details}")
            return details
            
        except Exception as e:
            print(f"❌ Error parsing apartment details: {e}")
            return {}

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

def get_phone_prefix(phone_number):
    """Extract first 2 digits for phone prefix selection"""
    if len(phone_number) >= 2:
        return phone_number[:2]
    return "05"  # Default fallback

def fill_single_ad(page, ad_data, test_mode=False):
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
        
        # Address (Адрес)
        if 'address' in apartment_details:
            print(f"📍 Filling address: {apartment_details['address']}")
            address_selectors = [
                'input[name="address"]',
                'input#address',
                'textarea[name="address"]'
            ]
            for selector in address_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.fill(selector, apartment_details['address'])
                        print("✅ Address filled successfully")
                        break
                except:
                    continue

        # Rooms (Комнаты)
        if 'rooms' in apartment_details:
            print(f"🚪 Filling rooms: {apartment_details['rooms']}")
            rooms_selectors = [
                'select[name="rooms"]',
                'select#rooms',
                'input[name="rooms"]'
            ]
            for selector in rooms_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        if selector.startswith('select'):
                            page.select_option(selector, value=apartment_details['rooms'])
                        else:
                            page.fill(selector, apartment_details['rooms'])
                        print("✅ Rooms filled successfully")
                        break
                except:
                    continue

        # Floor (Этаж)
        if 'floor' in apartment_details:
            print(f"🏢 Filling floor: {apartment_details['floor']}")
            floor_selectors = [
                'select[name="floor"]',
                'select#floor',
                'input[name="floor"]'
            ]
            for selector in floor_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        if selector.startswith('select'):
                            page.select_option(selector, value=apartment_details['floor'])
                        else:
                            page.fill(selector, apartment_details['floor'])
                        print("✅ Floor filled successfully")
                        break
                except:
                    continue

        # Furniture (Мебель)
        if 'furniture' in apartment_details:
            print(f"🛋️ Filling furniture: {apartment_details['furniture']}")
            furniture_selectors = [
                'select[name="furniture"]',
                'select#furniture',
                'select[name="mebel"]'
            ]
            for selector in furniture_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        furniture_value = 'да' if apartment_details['furniture'].lower() in ['да', 'yes', 'true'] else 'нет'
                        page.select_option(selector, label=furniture_value)
                        print("✅ Furniture filled successfully")
                        break
                except:
                    continue

        # Price (Цена)
        if 'price' in apartment_details:
            print(f"💰 Filling price: {apartment_details['price']}")
            price_selectors = [
                'input[name="price"]',
                'input#price',
                'input[type="number"]'
            ]
            for selector in price_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.fill(selector, apartment_details['price'])
                        print("✅ Price filled successfully")
                        break
                except:
                    continue

        time.sleep(2)

        # STEP 5: Ad text (Текст объявления)
        print("📝 Step 5: Filling ad text")
        ad_text_selectors = [
            'textarea[name="ad_text"]',
            'textarea#ad_text',
            'textarea.ad-text',
            'textarea:near(text("Текст объявления"))'
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

        # STEP 6: Image uploads (5 separate inputs)
        if test_mode:
            print(f"🖼️ Step 6: TEST MODE - Would upload {len(ad_data['images'])} images to 5 separate inputs")
            for i, img in enumerate(ad_data['images'][:5]):
                print(f"   📎 Would upload image {i+1}: {img['name']}")
        else:
            print(f"🖼️ Step 6: Uploading {len(ad_data['images'])} images to 5 separate inputs")
            temp_dir = "temp_images"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Download images temporarily
            downloaded_images = []
            for i, img in enumerate(ad_data['images'][:5]):  # Limit to 5 images
                temp_path = os.path.join(temp_dir, f"img_{i}_{img['name']}")
                if drive_client.download_image_file(img['id'], temp_path):
                    downloaded_images.append(temp_path)
                    print(f"✅ Downloaded: {img['name']}")

            # Upload to 5 separate file inputs
            for i in range(1, 6):  # Фото 1 through Фото 5
                if i-1 < len(downloaded_images):
                    try:
                        upload_selectors = [
                            f'input[name="photo[{i}]"]',
                            f'input[name="photo{i}"]',
                            f'input#photo{i}',
                            f'input[type="file"]:nth-of-type({i})'
                        ]
                        
                        for selector in upload_selectors:
                            if page.locator(selector).count() > 0:
                                page.set_input_files(selector, downloaded_images[i-1])
                                print(f"✅ Uploaded image {i}: {os.path.basename(downloaded_images[i-1])}")
                                break
                        else:
                            print(f"⚠️ File upload field {i} not found")
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

        # Phone number field
        phone_selectors = [
            'input[name="phone"]',
            'input#phone',
            'input.phone-number',
            'input[type="tel"]'
        ]
        
        for selector in phone_selectors:
            try:
                if page.locator(selector).count() > 0:
                    phone_without_prefix = ad_data['phone_number'][2:] if ad_data['phone_number'].startswith(phone_prefix) else ad_data['phone_number']
                    page.fill(selector, phone_without_prefix)
                    print("✅ Phone number filled successfully")
                    break
            except:
                continue

        time.sleep(1)

        # STEP 8: Email (hardcoded)
        print("📧 Step 8: Filling email: 111@gmail.com")
        email_selectors = [
            'input[name="email"]',
            'input#email',
            'input[type="email"]'
        ]
        
        for selector in email_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, '111@gmail.com')
                    print("✅ Email filled successfully")
                    break
            except:
                continue
        else:
            print("⚠️ Email field not found")

        time.sleep(1)

        # STEP 9: Agreement checkbox
        print("✅ Step 9: Checking agreement checkbox")
        agreement_selectors = [
            'input[type="checkbox"][name*="agree"]',
            'input[type="checkbox"]:near(text("пользовательское соглашение"))',
            'input#agreement',
            'input.agreement'
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

        # STEP 10: Submit button
        if test_mode:
            print("🧪 Step 10: TEST MODE - Would click 'Добавить объявление' button")
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:text("Добавить объявление")',
                '.submit-btn'
            ]
            
            for selector in submit_selectors:
                if page.locator(selector).count() > 0:
                    print(f"✅ Found submit button: {selector}")
                    break
            else:
                print("⚠️ Submit button not found")
        else:
            print("🚀 Step 10: Submitting form...")
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:text("Добавить объявление")',
                '.submit-btn'
            ]
            
            for selector in submit_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector)
                        print("✅ Form submitted successfully!")
                        time.sleep(5)  # Wait for submission
                        break
                except:
                    continue
            else:
                print("❌ Submit button not found")

        print(f"✅ Completed processing ad for phone: {ad_data['phone_number']}")
        return True

    except Exception as e:
        print(f"❌ Error filling form for {ad_data['phone_number']}: {e}")
        return False

def main():
    """Main function - TEST MODE with local page.html"""
    print("🧪 ORBITA FORM FILLER - TEST MODE")
    print("=" * 50)
    print("📁 Using local page.html file for testing")
    print("🔗 Will NOT submit to live website")
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
    except Exception as e:
        print(f"❌ Could not connect to Google Drive: {e}")
        print("ℹ️ You can still test the form filling with dummy data")
        drive_client = None

    # Get ad folders from Google Drive
    ad_folders = []
    if drive_client:
        try:
            ad_folders = drive_client.find_datetime_folders("ad")  # Use 'ad' folder
            if not ad_folders:
                print("⚠️ No datetime folders found in 'ad' folder")
                print("📝 Using dummy data for testing")
        except Exception as e:
            print(f"❌ Error accessing Google Drive: {e}")
            print("📝 Using dummy data for testing")

    # If no Google Drive data, use dummy data for testing
    if not ad_folders:
        ad_folders = [{
            'name': 'ad/20250523/1445',
            'id': 'dummy_id_1',
            'date': '20250523',
            'time': '1445',
            'path': 'ad/20250523/1445'
        }]

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
        input("Press Enter to exit...")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        
        # Create context with proper permission handling
        context = browser.new_context(
            permissions=[],  # No permissions granted initially
            geolocation=None,
            ignore_https_errors=True,
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8'
            }
        )
        
        # Explicitly deny notifications
        context.grant_permissions([])
        
        page = context.new_page()
        
        # Handle any popup dialogs that appear
        page.on("dialog", lambda dialog: dialog.dismiss())
        
        # Suppress JavaScript errors in console to avoid interference
        page.on("pageerror", lambda error: print(f"🔇 Suppressed JS error: {error}"))
        
        try:
            # Load local HTML file
            current_dir = os.getcwd()
            local_file_path = f"file://{current_dir}/page.html"
            print(f"\n🌐 Loading local file: {local_file_path}")
            
            page.goto(local_file_path)
            page.wait_for_load_state('networkidle')
            print("✅ Local page loaded successfully")

            # Dismiss notifications with a more gentle approach
            dismiss_notifications(page)

            # Process each new ad folder
            for i, folder in enumerate(new_ads, 1):
                print(f"\n📁 Processing folder {i}/{len(new_ads)}: {folder['path']}")
                
                # Get ad data from Google Drive or use dummy data
                if drive_client and folder['id'] != 'dummy_id_1':
                    ad_data = drive_client.get_folder_contents(folder['id'])
                    if not ad_data:
                        print(f"⚠️ No data found in folder {folder['path']}")
                        continue
                else:
                    # Dummy data for testing
                    ad_data = {
                        'phone_file': {'name': '0501234567.txt'},
                        'ad_text': f'Test ad text for {folder["path"]}\n\nThis is a test apartment listing with beautiful views and modern amenities. Located in a prime location with easy access to transportation.',
                        'images': [
                            {'name': 'apartment1.jpg', 'id': 'dummy_img1'},
                            {'name': 'apartment2.png', 'id': 'dummy_img2'},
                            {'name': 'apartment3.jpg', 'id': 'dummy_img3'}
                        ],
                        'phone_number': '0501234567',
                        'apartment_details': {
                            'address': 'Ришон Ле-Цион, Ротшильд 12-1',
                            'rooms': '4.5',
                            'floor': '2',
                            'furniture': 'Да',
                            'price': '2000000'
                        }
                    }

                # Fill the form
                success = fill_single_ad(page, ad_data, test_mode=True)
                
                if success:
                    print(f"✅ Successfully processed: {folder['path']}")
                    # Mark as processed in test mode too (for testing the logging)
                    logger.mark_as_processed(folder['path'])
                else:
                    print(f"❌ Failed to process: {folder['path']}")

                # Wait between ads (if processing multiple)
                if i < len(new_ads):
                    print(f"\n⏳ Waiting 5 seconds before next ad...")
                    time.sleep(5)
                    # Reload page for next ad
                    page.reload()
                    page.wait_for_load_state('networkidle')

        except Exception as e:
            print(f"❌ Error during form filling: {e}")
        finally:
            # Show final statistics
            final_stats = logger.get_stats()
            print(f"\n📊 FINAL STATISTICS:")
            print(f"   📋 Total processed ads: {final_stats['total_processed']}")
            print(f"   📄 Log file: {final_stats['log_file']}")
            
            print("\n🏁 Test completed!")
            print("Press Enter to close browser...")
            input()
            browser.close()

if __name__ == "__main__":
    main() 