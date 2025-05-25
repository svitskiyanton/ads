# Orbita Form Filler - Complete User Guide

## 🎯 Overview

The **Orbita Form Filler** is an advanced automation script for posting apartment rental ads on Orbita.co.il. It features enterprise-grade security measures, Tor IP rotation, reCAPTCHA solving, and Google Drive integration.

## 🏗️ System Architecture

```
Google Drive (ads) → Script → Tor Network → Orbita.co.il
     ↓              ↓           ↓             ↓
   Ad Data    Form Filling  IP Rotation   Published Ads
```

## 📋 Features

### 🔐 **Security & Anonymity**
- ✅ **Tor IP Rotation** - Different IP for each ad
- ✅ **Enhanced Security Workflow** - Logout/wait/IP change between ads
- ✅ **Anti-Detection** - Human-like behavior simulation
- ✅ **Session Isolation** - Fresh authentication for each ad

### 🤖 **Automation**
- ✅ **Google Drive Integration** - Automatic ad data retrieval
- ✅ **reCAPTCHA Solving** - Automatic captcha handling via 2captcha
- ✅ **Form Auto-Fill** - Complete apartment listing automation
- ✅ **Image Upload** - Automatic photo handling (up to 5 images)

### 📊 **Management**
- ✅ **Progress Tracking** - Processed ads logging
- ✅ **Error Handling** - Robust error recovery
- ✅ **Statistics** - Success/failure reporting
- ✅ **Duplicate Prevention** - Skip already processed ads

## ⚙️ Configuration Options

### 📁 **config.py Settings**

#### 🔑 **Authentication & API Keys**
```python
# 2captcha API Configuration (REQUIRED)
CAPTCHA_API_KEY = "your_2captcha_api_key_here"

# Orbita.co.il Account Credentials (REQUIRED)
ORBITA_LOGIN_EMAIL = "your_email@example.com"
ORBITA_LOGIN_PASSWORD = "your_password"
```

#### 🌐 **Browser Settings**
```python
# Browser behavior
BROWSER_HEADLESS = False        # True = hidden browser, False = visible
BROWSER_SLOW_MO = 2000         # Milliseconds between actions (1000-3000)

# Form filling delays (in seconds)
STEP_DELAY = 2                 # General delay between steps
RECAPTCHA_WAIT = 3             # Wait time for reCAPTCHA to load
FORM_LOAD_WAIT = 3             # Wait time for form to load
```

#### 🔒 **Tor IP Rotation Settings**
```python
USE_TOR_IP_ROTATION = True     # Enable/disable Tor IP rotation
TOR_IP_CHANGE_INTERVAL = 3     # Change IP every N ads (0 = disabled)
TOR_STARTUP_DELAY = 15         # Seconds to wait after starting Tor
TOR_IP_CHANGE_DELAY = 5        # Seconds to wait after changing IP
```

#### 🛡️ **Enhanced Security Workflow**
```python
LOGOUT_BETWEEN_ADS = True      # Logout after each ad for security
WAIT_AFTER_LOGOUT = 180        # Wait time in seconds after logout (3 minutes)
CHANGE_IP_AFTER_LOGOUT = True  # Change IP after logout (requires Tor)
```

#### 📁 **Google Drive Settings**
```python
GOOGLE_DRIVE_PARENT_FOLDER = "ad"  # Parent folder name in Google Drive
```

#### 🐛 **Debug Settings**
```python
DEBUG_SCREENSHOTS = False     # Take screenshots for debugging
DEBUG_CONSOLE_LOGS = True     # Show console logs
```

## 📁 **Google Drive Folder Structure**

### Required Structure:
```
📁 ad/
  └── 📁 20240101/     # Date folder (YYYYMMDD)
      └── 📁 1430/     # Time folder (HHMM)
          ├── 📄 params.txt        # Apartment details
          ├── 📄 054123456.txt     # Ad text (phone in filename)
          ├── 🖼️ image1.jpg       # Photos (up to 5)
          ├── 🖼️ image2.jpg
          └── 🖼️ image3.jpg
```

### File Formats:

#### **params.txt** (Line-based format):
```
Line 1: [ignored]
Line 2: Address (e.g., "HaShalom 25, Rishon LeZion")
Line 3: [ignored]
Line 4: Rooms (e.g., "3", "2.5", "4+")
Line 5: [ignored]
Line 6: Floor (e.g., "2", "10+")
Line 7: [ignored]
Line 8: Furniture (e.g., "да", "нет", "частично")
Line 9: [ignored]
Line 10: Price (e.g., "5500", "4200")
```

#### **Phone Number Text File** (e.g., 054123456.txt):
- Filename must contain the phone number
- Content is the ad text/description
- Phone will be extracted from filename

#### **Image Files**:
- Formats: `.jpg`, `.jpeg`, `.png`
- Up to 5 images per ad
- Will be uploaded in alphabetical order

## 🚀 **Setup Instructions**

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Configure API Keys**
Edit `config.py`:
```python
# Get from https://2captcha.com/
CAPTCHA_API_KEY = "your_actual_api_key"

# Your Orbita.co.il account
ORBITA_LOGIN_EMAIL = "your_email@example.com"
ORBITA_LOGIN_PASSWORD = "your_password"
```

### 3. **Setup Google Drive API**
1. Create project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Drive API
3. Create OAuth2 credentials
4. Download as `credentials.json` in script directory
5. Run script first time to authorize (creates `token.json`)

### 4. **Setup Tor (Optional but Recommended)**
- **Windows**: Script auto-downloads Tor Expert Bundle
- **Linux**: Script auto-installs via `apt`
- Set `USE_TOR_IP_ROTATION = True` in config

### 5. **Prepare Ad Data**
Create folder structure in Google Drive as shown above.

## 📊 **Usage Examples**

### **Basic Usage (No Tor)**
```python
# config.py
USE_TOR_IP_ROTATION = False
LOGOUT_BETWEEN_ADS = False
```
```bash
python orbita_form_filler.py
```

### **Secure Usage (With Tor)**
```python
# config.py
USE_TOR_IP_ROTATION = True
LOGOUT_BETWEEN_ADS = True
WAIT_AFTER_LOGOUT = 180
CHANGE_IP_AFTER_LOGOUT = True
```
```bash
python orbita_form_filler.py
```

### **Conservative (Long waits)**
```python
# config.py
WAIT_AFTER_LOGOUT = 300        # 5 minutes
BROWSER_SLOW_MO = 3000         # Slower actions
```

### **Aggressive (Fast posting)**
```python
# config.py
WAIT_AFTER_LOGOUT = 120        # 2 minutes
BROWSER_SLOW_MO = 1000         # Faster actions
```

## 🧪 **Testing Commands**

### **Test Tor Integration**
```bash
python test_tor_improved.py
```

### **Test Enhanced Workflow**
```bash
python test_enhanced_workflow.py
```

### **Test IP Comparison**
```bash
python test_ip_comparison.py
```

## ⏰ **Performance & Timing**

### **Processing Time per Ad:**

#### Without Enhanced Security:
- Ad processing: 2-3 minutes
- **Total**: ~2-3 minutes per ad

#### With Enhanced Security Workflow:
- Ad processing: 2-3 minutes
- Logout/wait/IP change: 3-4 minutes
- **Total**: ~6-7 minutes per ad

### **Batch Processing Estimates:**
- **5 ads**: 10-35 minutes (depending on security settings)
- **10 ads**: 20-70 minutes
- **20 ads**: 40 minutes - 2.5 hours

## 🔧 **Advanced Configuration**

### **Browser Arguments**
The script uses these anti-detection arguments:
```python
browser_args = [
    '--no-blink-features=AutomationControlled',
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--disable-extensions',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-default-apps',
    '--disable-popup-blocking'
]
```

### **User Agent**
```python
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
```

### **Viewport Settings**
```python
viewport = {'width': 1366, 'height': 768}  # Common screen resolution
```

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **Authentication Failures**
```
❌ Error: Login failed
```
**Solution**: Check email/password in `config.py`

#### **reCAPTCHA Issues**
```
❌ Error: Failed to solve reCAPTCHA
```
**Solutions**:
- Verify `CAPTCHA_API_KEY` is correct
- Check 2captcha balance
- Ensure internet connection

#### **Google Drive Errors**
```
❌ Error: No datetime folders found
```
**Solutions**:
- Check folder structure matches required format
- Verify `credentials.json` is present
- Re-authorize with `rm token.json`

#### **Tor Connection Issues**
```
❌ Error: Could not verify IP
```
**Solutions**:
- Check internet connection
- Wait longer for Tor circuits (increase `TOR_STARTUP_DELAY`)
- Disable Tor temporarily: `USE_TOR_IP_ROTATION = False`

#### **Form Filling Errors**
```
❌ Error: Element not found
```
**Solutions**:
- Increase `BROWSER_SLOW_MO` (slower actions)
- Check if Orbita.co.il website structure changed
- Ensure account is properly authenticated

### **Log Files**

#### **Processed Ads Log**
- **File**: `processed_ads.log`
- **Purpose**: Tracks completed ads to prevent duplicates
- **Format**: `ad_path # Processed on timestamp`

#### **Debug Logs**
Console output shows detailed progress:
- ✅ Success indicators
- ❌ Error messages  
- ⏳ Wait/progress indicators
- 🔄 IP change notifications

## 📈 **Best Practices**

### **Security**
1. **Always use Tor** for IP anonymization
2. **Enable enhanced workflow** for maximum stealth
3. **Use realistic timing** - avoid too fast posting
4. **Monitor success rates** - adjust if failures increase

### **Reliability**
1. **Test configuration** before large batches
2. **Monitor 2captcha balance** before runs
3. **Check Google Drive structure** before running
4. **Have backup credentials** ready

### **Performance**
1. **Start with small batches** (2-3 ads) to test
2. **Monitor system resources** during long runs
3. **Schedule large runs** during off-peak hours
4. **Use stable internet connection**

## 🔒 **Security Considerations**

### **Account Safety**
- Use dedicated Orbita account for automation
- Don't exceed reasonable posting frequency
- Monitor for account warnings/suspensions

### **IP Anonymization**
- Always verify Tor is working correctly
- Check for IP leaks before production runs
- Monitor for IP-based blocking

### **Data Protection**
- Keep API keys secure
- Don't commit credentials to version control
- Use strong passwords for Orbita account

## 📞 **Support & Maintenance**

### **Regular Maintenance**
- Update Chrome/Chromium regularly
- Check for Orbita.co.il website changes
- Monitor 2captcha service status
- Update Tor regularly

### **Monitoring**
- Watch success/failure rates
- Check IP rotation effectiveness
- Monitor authentication success
- Track processing times

---

## 🎯 **Quick Start Checklist**

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure `config.py` with API keys and credentials
- [ ] Setup Google Drive API (`credentials.json`)
- [ ] Create ad folders in Google Drive
- [ ] Test Tor integration: `python test_tor_improved.py`
- [ ] Run small test batch: 1-2 ads
- [ ] Monitor logs and success rates
- [ ] Scale up to production batches

**Ready to automate your Orbita.co.il ad posting with enterprise-grade security! 🚀** 