# 🏠 Orbita Automated Form Filler

Automate posting classified ads to Orbita from Google Drive with smart logging and duplicate prevention.

## 📋 Overview

This system automatically:
- ✅ Connects to your Google Drive
- ✅ Finds ad data in `ad/YYYYMMDD/HHMM` folder structure
- ✅ Extracts phone numbers, ad text, and images
- ✅ Fills Orbita form automatically
- ✅ Tracks processed ads to prevent duplicates
- ✅ Supports both testing and production modes

## 📁 Google Drive Folder Structure

```
📁 Your Google Drive Root/
  📁 ad/                    ← Main folder
    📁 20250523/            ← Date folder (YYYYMMDD)
      📁 1445/              ← Time folder (HHMM) = 1 ad
        📄 0501234567.txt   ← Phone number + ad text
        🖼️ image1.jpg       ← Images (up to 5)
        🖼️ image2.png
        🖼️ image3.jpg
      📁 1511/              ← Another ad
        📄 0527891234.txt
        🖼️ apartment1.jpg
    📁 20250522/            ← Another date
      📁 1112/
        📄 0541239876.txt
        🖼️ photo1.jpg
      📁 0912/
        📄 0525551234.txt
        🖼️ house1.png
        🖼️ house2.jpg
```

## 📄 File Format

### 📱 Phone Number Files
- **Filename**: `{phone_number}.txt`
- **Content**: The actual ad text

Example: `0501234567.txt`
```
Beautiful apartment for sale in Rishon LeZion

3 rooms, 2nd floor, renovated kitchen, close to shopping centers and schools. 
Excellent condition, ready to move in!

Price: Contact for details
```

### 🖼️ Images
- Supported formats: `.jpg`, `.jpeg`, `.png`
- Up to 5 images per ad
- Any filename (will be uploaded in order found)

## 🚀 Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m playwright install
```

### 2. Setup Google Drive API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Google Drive API → Create OAuth2 credentials
3. Download `credentials.json` to this folder
4. See `SETUP_GUIDE.md` for detailed steps

### 3. Create Folder Structure
Create the `ad` folder in your Google Drive root and organize your ads.

## 🎮 Usage

### 🧪 Test Mode (Recommended First)
Test with local HTML file - **no real submissions**:

```bash
python orbita_form_filler_test.py
```

**Features:**
- ✅ Uses your real Google Drive data
- ✅ Tests form filling logic
- ✅ Uses local `page.html` file
- ❌ **Does NOT submit to live website**

### 🚀 Production Mode
Submit to live Orbita website:

```bash
python orbita_form_filler.py
```

**Features:**
- ⚠️ **SUBMITS TO LIVE WEBSITE**
- ✅ Processes real ads from Google Drive
- ✅ Asks for confirmation before starting
- ✅ Logs processed ads automatically

### 🎯 Simple Local Test (No Google Drive)
Quick test with dummy data:

```bash
python simple_local_test.py
```

## 📊 Logging System

### 📄 Log File: `processed_ads.log`
Tracks all successfully processed ads to prevent duplicates:

```
ad/20250523/1445 # Processed on 2025-01-23 14:45:12
ad/20250523/1511 # Processed on 2025-01-23 15:11:05
ad/20250522/1112 # Processed on 2025-01-23 15:15:30
```

### 🔄 Smart Duplicate Prevention
- Automatically skips already processed ads
- Shows statistics: new vs. skipped ads
- Logs timestamp for each processed ad

## 🛠️ Form Filling Logic

### 1. Board Selection
- **Target**: "Квартиры - продам"
- **Method**: Multiple selector strategies + fallback clicks

### 2. City Selection  
- **Target**: "Ришон ле Цион"
- **Method**: Label matching + value selection

### 3. Phone Number
- **Prefix**: First 2 digits (05, 02, 03, etc.)
- **Number**: Remaining digits
- **Source**: Extracted from filename

### 4. Ad Text
- **Source**: Content of `.txt` file
- **Target**: Main textarea field

### 5. Images
- **Download**: Temporarily from Google Drive
- **Upload**: To form file inputs
- **Cleanup**: Automatic after processing

### 6. Agreement
- **Action**: Check "пользовательское соглашение"

### 7. Submit
- **Test Mode**: Just locate button (no click)
- **Production**: Actually submit form

## 📁 File Structure

```
📁 Project Directory/
  📄 orbita_form_filler.py           ← Main production script
  📄 orbita_form_filler_test.py      ← Test script (local HTML)
  📄 simple_local_test.py            ← Simple test (no Google Drive)
  📄 requirements.txt                ← Dependencies
  📄 SETUP_GUIDE.md                  ← Google Drive setup guide
  📄 README.md                       ← This file
  📄 page.html                       ← Local form for testing
  📄 credentials.json                ← Your OAuth2 credentials (add this)
  📄 token.json                      ← Auto-generated auth token
  📄 processed_ads.log               ← Auto-generated log file
  📁 temp_images/                    ← Temporary image downloads
```

## 🔧 Configuration

### Phone Prefix Mapping
Automatically detects phone prefixes:
- `05` → Israeli mobile
- `02`, `03`, `04`, etc. → Area codes
- Default fallback: `05`

### Timing
- **Test Mode**: 1000ms slow-mo
- **Production**: 2000ms slow-mo
- **Between Ads**: 10 seconds wait

## 🚨 Important Notes

### ⚠️ Before First Run
1. **Test Mode First**: Always run test version first
2. **Check Log File**: Review `processed_ads.log` 
3. **Verify Data**: Confirm Google Drive structure
4. **Small Batch**: Start with 1-2 ads for testing

### 🔒 Security
- OAuth2 authentication (no hardcoded tokens)
- Local credential storage
- Read-only Google Drive access

### 📊 Monitoring
- Real-time console output
- Success/failure statistics
- Comprehensive error messages
- Progress indicators

## 🐛 Troubleshooting

### Common Issues

1. **"credentials.json not found"**
   - Download OAuth2 credentials from Google Cloud Console
   - Place in project directory

2. **"Parent folder 'ad' not found"**
   - Create `ad` folder in Google Drive root
   - Ensure exact spelling

3. **"No datetime folders found"**
   - Check folder naming: `YYYYMMDD/HHMM`
   - Verify folder hierarchy: `ad/20250523/1445/`

4. **Form selectors not found**
   - Website structure may have changed
   - Run test mode to debug selectors
   - Update selector arrays in code

### 🔍 Debug Mode
Add print statements or enable verbose logging for troubleshooting.

## 📈 Statistics Example

```
🧪 ORBITA FORM FILLER - TEST MODE
==================================================
📁 Using local page.html file for testing
🔗 Will NOT submit to live website
📁 Looking for ads in 'ad' folder structure
==================================================
📋 Previously processed ads: 3
🔌 Connecting to Google Drive...
✅ Google Drive API connected successfully!
✅ Found parent folder: ad
✅ Found 5 datetime folders in 'ad'
📊 Found 5 ad folders to process
✅ New ads to process: 2
⏭️ Skipped (already processed): 3

📋 Skipped ads:
   ⏭️ ad/20250522/0912
   ⏭️ ad/20250522/1112
   ⏭️ ad/20250523/1445
```

This system ensures efficient, safe, and reliable automated posting with full tracking and duplicate prevention! 🎉 