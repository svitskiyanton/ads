# Orbita Automated Ad Processor - Setup Guide

## 📋 Prerequisites

1. **Python 3.7+** installed
2. **Google Account** with access to Google Drive
3. **Google Cloud Console** access

## 🚀 Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Drive API

#### Step 2.1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project name/ID

#### Step 2.2: Enable Google Drive API
1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google Drive API"
3. Click on it and press **Enable**

#### Step 2.3: Create Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - Choose **External** user type
   - Fill in required fields (App name, User support email, etc.)
   - Add your email to test users
4. For OAuth client ID:
   - Application type: **Desktop application**
   - Name: "Orbita Ad Processor" (or any name)
5. Download the JSON file
6. **Rename it to `credentials.json`** and place it in the same folder as the script

### 3. Organize Your Google Drive

Create folders in your Google Drive with this structure:
```
📁 Your Drive
  📁 20250123\1445  ← DateTime format folders
    📄 0521234567.txt   ← Phone number as filename
    🖼️ photo1.jpg      ← Images for the ad
    🖼️ photo2.png
  📁 20250123\1511
    📄 0541234567.txt
    🖼️ image1.jpg
    🖼️ image2.jpg
```

**Folder naming convention:**
- Format: `YYYYMMDD\HHMM`
- Example: `20250523\1445` (May 23, 2025 at 14:45)

**File naming convention:**
- Text file: `[phonenumber].txt` (e.g., `0521234567.txt`)
- Images: any `.jpg`, `.jpeg`, `.png` files

## 📝 Usage

### Run the Script
```bash
python orbita_form_filler.py
```

### First Run
- The script will open a browser for Google authentication
- Sign in with your Google account
- Grant permission to access Google Drive
- The script will save authentication tokens for future use

### What the Script Does

1. **🔍 Scans Google Drive** for datetime-formatted folders
2. **📁 Processes each folder:**
   - Downloads text file for ad content
   - Downloads images for photo uploads
   - Extracts phone number from filename
3. **🌐 Fills Orbita form:**
   - Board: "Квартиры - продам"
   - City: "Ришон ле Цион"
   - Ad text from the text file
   - Uploads images (up to 5)
   - Phone number with area code extraction
   - Checks agreement checkbox
   - Submits the form
4. **🔄 Repeats** for each valid folder

## 📂 File Structure

After setup, your directory should look like:
```
📁 Your Project Folder
  📄 orbita_form_filler.py
  📄 requirements.txt
  📄 credentials.json        ← Google API credentials
  📄 token.json             ← Auto-created after first auth
  📁 temp_ads/              ← Auto-created temp folder
  📄 SETUP_GUIDE.md
```

## ⚙️ Configuration

### Phone Number Processing
- **Area code**: First 2 digits (e.g., "05" from "0521234567")
- **Number**: Remaining digits (e.g., "21234567")

### Supported Image Formats
- `.jpg`, `.jpeg`, `.png`
- Maximum 5 images per ad

### Text File Encoding
- The script tries UTF-8 first, then CP1251 for Hebrew text

## 🔧 Troubleshooting

### Common Issues

1. **"credentials.json not found"**
   - Download OAuth credentials from Google Cloud Console
   - Rename to `credentials.json`

2. **"No datetime folders found"**
   - Check folder naming: `YYYYMMDD\HHMM`
   - Ensure folders are in your Google Drive root or specify parent folder

3. **"Browser not opening"**
   - Check if Playwright browsers are installed: `python -m playwright install`

4. **"Form elements not found"**
   - Website might have changed
   - Check browser console for errors
   - Update selectors if needed

### Debug Mode
To inspect form elements, modify the script to add:
```python
# Set headless=False and slow_mo for debugging
browser = p.chromium.launch(headless=False, slow_mo=2000)
```

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your Google Drive folder structure
3. Ensure credentials.json is properly configured
4. Make sure all dependencies are installed

## ⚠️ Important Notes

- **Test first**: Run with a single folder to verify everything works
- **Rate limiting**: The script includes delays between submissions
- **Manual review**: Always verify the form is filled correctly before submission
- **Backup**: Keep backups of your ad content and images 