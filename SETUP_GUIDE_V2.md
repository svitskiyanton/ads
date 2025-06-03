# Orbita Form Filler v2.0 - Complete Setup Guide

## 🎯 Overview

The **Orbita Form Filler v2.0** is an enhanced automation script that includes:

- ✅ **Auto-registration** of new accounts before posting ads
- ✅ **OpenAI GPT-4.1 nano integration** for intelligent parameter extraction
- ✅ **New Google Drive structure** for organized ad management
- ✅ **Enhanced security** with Tor IP rotation
- ✅ **Smart form filling** with reCAPTCHA solving

## 🔧 Prerequisites

### **Required Accounts & API Keys**

1. **2captcha Account**
   - Sign up at: https://2captcha.com/
   - Get API key from dashboard
   - Minimum balance: $5-10 recommended

2. **OpenAI Account** (NEW)
   - Sign up at: https://platform.openai.com/
   - Get API key from API keys section
   - GPT-4.1 nano pricing: $0.100/1M input tokens

3. **Google Cloud Project**
   - Create project at: https://console.cloud.google.com/
   - Enable Google Drive API
   - Create OAuth2 credentials

## 📦 Installation

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Install Playwright Browsers**
```bash
python -m playwright install
```

### **3. Google Drive API Setup**

#### **Step 1: Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Orbita Form Filler"
3. Enable Google Drive API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Desktop application"
6. Download JSON as `credentials.json`

#### **Step 2: Place Credentials**
```bash
# Place in script directory
credentials.json
```

### **4. Configure API Keys**

Edit `config.py`:

```python
# REQUIRED - 2captcha API key
CAPTCHA_API_KEY = "your_actual_2captcha_api_key"

# REQUIRED - OpenAI API key  
OPENAI_API_KEY = "your_actual_openai_api_key"
```

## 📁 Google Drive Structure Setup

### **New Folder Structure**
```
📁 Shared with me/
  └── 📁 Авто реклама/
      └── 📁 Ришон Лецион/
          └── 📁 ПРОДАЖА/
              ├── 📁 Ad_Folder_1/
              │   ├── 📄 apartment_description.gdoc
              │   ├── 🖼️ photo1.jpg
              │   ├── 🖼️ photo2.jpg
              │   └── 🖼️ photo3.jpg
              └── 📁 Ad_Folder_2/
                  ├── 📄 listing_text.gdoc
                  └── 🖼️ image1.jpg
```

### **File Requirements**

#### **Google Document** (One per folder)
- **Content**: Full apartment listing text in Russian
- **Example**:
```
Ришон Лецион
Продажа квартиры 
4 комнаты, включая МАМАД (комнату безопасности)  
Район НАХЛАД ИУДА
* Шикарный вид из окон
* Очень высокий этаж
* Родительская спальня с с/у
* Большая гостиная
* Солнечный балкон- 19 м
* Двойная парковка 
* В квартире никто не жил
Цена: 2,450,000 ₪
```

#### **Images** (Optional, max 5 per folder)
- **Formats**: `.jpg`, `.jpeg`, `.png`
- **Size**: Under 5MB each
- **Order**: Alphabetical by filename

## ⚙️ Configuration Options

### **Security Levels**

#### **Maximum Security (Recommended)**
```python
USE_TOR_IP_ROTATION = True
TOR_IP_CHANGE_INTERVAL = 2       # Change IP every 2 ads
WAIT_BETWEEN_ADS = 300           # 5 minutes between ads
BROWSER_SLOW_MO = 3000           # Slow, human-like actions
```

#### **Balanced Performance**
```python
USE_TOR_IP_ROTATION = True
TOR_IP_CHANGE_INTERVAL = 3       # Change IP every 3 ads
WAIT_BETWEEN_ADS = 180           # 3 minutes between ads (default)
BROWSER_SLOW_MO = 2000           # Normal speed
```

#### **Fast Mode (Less Secure)**
```python
USE_TOR_IP_ROTATION = False
TOR_IP_CHANGE_INTERVAL = 0       # No IP changes
WAIT_BETWEEN_ADS = 120           # 2 minutes between ads
BROWSER_SLOW_MO = 1000           # Faster actions
```

## 🧪 Testing

### **1. Run Component Tests**
```bash
python test_new_algorithm.py
```

This tests:
- ✅ OpenAI parameter extraction
- ✅ Google Drive connection
- ✅ Registration page detection
- ✅ 2captcha service
- ✅ Email generation

### **2. Expected Test Results**
```
🧪 ORBITA FORM FILLER V2 - COMPONENT TESTS
==========================================

Email Generation................. ✅ PASSED
OpenAI Extraction................ ✅ PASSED
Google Drive Connection.......... ✅ PASSED
Registration Page................ ✅ PASSED
2captcha Service................. ✅ PASSED

Total: 5/5 tests passed
🎉 All tests passed! Ready to run main script.
```

## 🚀 Usage

### **1. First Run (Authorization)**
```bash
python orbita_form_filler_v2.py
```

- Will prompt for Google Drive authorization
- Will auto-register new Orbita account
- Will process all available ads

### **2. Regular Usage**
```bash
python orbita_form_filler_v2.py
```

## 📊 What Happens During Execution

### **Phase 1: Initialization**
```
🚀 Initializing Orbita Form Filler v2...
🌐 Starting Tor (if enabled)...
✅ Google Drive authenticated
✅ OpenAI configured
```

### **Phase 2: Account Registration**
```
🔐 Starting account registration...
📧 Generated email: abc1234@xyz9876543.com
✅ Account registered and logged in
```

### **Phase 3: Ad Processing**
```
📁 Getting ad folders from Google Drive...
📊 Found 5 ad folders

📂 Processing folder 1/5: Apartment_Luxury
📄 Retrieved ad text (1247 characters)
✅ Extracted parameters: {'rooms': '4', 'district': 'НАХЛАД ИУДА', 'price': '2450000'}
🖼️ Downloaded 3 images
📝 Filling Orbita form...
📤 Uploading 3 images...
🤖 Solving reCAPTCHA...
✅ Form submitted successfully
⏳ Waiting 180 seconds before next ad...
```

### **Phase 4: Final Statistics**
```
📊 FINAL STATISTICS
==================
✅ Successfully processed: 4
❌ Failed: 1
⏭️ Skipped (already processed): 0
📧 Account used: abc1234@xyz9876543.com
```

## 🔍 Parameter Extraction Examples

### **Input Text**:
```
Ришон Лецион
РЕМЕЗ
Продается квартира (очень большая -137 м)
* 5 комнат
* Комната безопасности (мамад)
* 2 туалета
* Балкон -14 м
* Лифт
Цена: 1,890,000 ₪
```

### **Extracted Parameters**:
```json
{
  "rooms": "5",
  "district": "РЕМЕЗ", 
  "price": "1890000"
}
```

## 🚨 Troubleshooting

### **Common Issues**

#### **OpenAI API Errors**
```
❌ OpenAI extraction failed: Incorrect API key
```
**Solution**: Check `OPENAI_API_KEY` in `config.py`

#### **Google Drive Path Not Found**
```
❌ Folder not found: ПРОДАЖА
```
**Solutions**:
- Verify exact folder names (case-sensitive)
- Check folder sharing permissions
- Ensure path: `Shared with me/Авто реклама/Ришон Лецион/ПРОДАЖА`

#### **Registration Failed**
```
❌ Registration may have failed
```
**Solutions**:
- Check 2captcha balance
- Verify internet connection
- Try different browser settings

#### **No Google Docs Found**
```
❌ No Google Doc found in folder
```
**Solutions**:
- Ensure each ad folder contains at least one Google Doc
- Check file sharing permissions
- Verify Google Doc is not empty

### **Debug Mode**

Enable detailed logging:
```python
DEBUG_CONSOLE_LOGS = True
DEBUG_SCREENSHOTS = True  # Takes screenshots on errors
```

## 📈 Performance Optimization

### **Batch Processing Tips**

1. **Start Small**: Test with 2-3 ads first
2. **Monitor Resources**: Check CPU/memory usage
3. **Stable Internet**: Ensure reliable connection
4. **Off-Peak Hours**: Run during low-traffic times

### **Cost Optimization**

1. **OpenAI Usage**: ~$0.01-0.02 per ad (GPT-4.1 nano)
2. **2captcha Usage**: ~$0.001-0.003 per reCAPTCHA
3. **Total Cost**: ~$0.02-0.05 per ad

## 🔒 Security Best Practices

### **Account Safety**
- Each run creates fresh account (no reuse)
- Tor IP rotation for anonymity
- Human-like timing between actions

### **API Key Security**
- Never commit `config.py` with real keys
- Use environment variables in production
- Regularly rotate API keys

### **Rate Limiting**
- Minimum 3 minutes between ads
- IP changes every 2-3 ads
- Respect website terms of service

## 📚 File Structure

```
orbita-form-filler-v2/
├── config.py                    # Configuration file
├── orbita_form_filler_v2.py    # Main script
├── test_new_algorithm.py       # Component tests
├── requirements.txt            # Dependencies
├── credentials.json            # Google Drive OAuth (you create)
├── token.json                 # Google Drive token (auto-created)
├── processed_ads_v2.log       # Processed ads log
└── SETUP_GUIDE_V2.md          # This guide
```

## 🎯 Quick Start Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure API keys in `config.py`
- [ ] Setup Google Drive API (`credentials.json`)
- [ ] Create folder structure in Google Drive
- [ ] Run tests: `python test_new_algorithm.py`
- [ ] Test with 1-2 ads: `python orbita_form_filler_v2.py`
- [ ] Scale up to production batches

---

**🚀 Ready to automate your Orbita.co.il apartment listings with AI-powered intelligence!** 