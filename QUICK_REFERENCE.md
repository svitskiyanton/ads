# Orbita Form Filler - Quick Reference

## 🚀 Essential Commands

```bash
# Main script (production mode)
python orbita_form_filler.py

# Test Tor integration
python test_tor_improved.py

# Test enhanced security workflow
python test_enhanced_workflow.py

# Test IP comparison (real vs Tor)
python test_ip_comparison.py
```

## ⚙️ Key Configuration Options

### 📝 **config.py - Must Configure**
```python
# REQUIRED - Get from https://2captcha.com/
CAPTCHA_API_KEY = "your_2captcha_api_key"

# REQUIRED - Your Orbita.co.il account
ORBITA_LOGIN_EMAIL = "your_email@example.com"
ORBITA_LOGIN_PASSWORD = "your_password"
```

### 🔒 **Security Levels**

#### **Maximum Security (Recommended)**
```python
USE_TOR_IP_ROTATION = True
LOGOUT_BETWEEN_ADS = True
WAIT_AFTER_LOGOUT = 300          # 5 minutes
CHANGE_IP_AFTER_LOGOUT = True
BROWSER_SLOW_MO = 3000           # Slower actions
```

#### **Balanced Security**
```python
USE_TOR_IP_ROTATION = True
LOGOUT_BETWEEN_ADS = True
WAIT_AFTER_LOGOUT = 180          # 3 minutes (default)
CHANGE_IP_AFTER_LOGOUT = True
BROWSER_SLOW_MO = 2000           # Default speed
```

#### **Fast Mode (Less Secure)**
```python
USE_TOR_IP_ROTATION = False
LOGOUT_BETWEEN_ADS = False
WAIT_AFTER_LOGOUT = 60           # 1 minute
BROWSER_SLOW_MO = 1000           # Faster actions
```

## 📁 **Google Drive Structure**

```
📁 ad/
  └── 📁 20240315/               # Date: YYYYMMDD
      └── 📁 1430/               # Time: HHMM
          ├── 📄 params.txt      # Line 2=address, 4=rooms, 6=floor, 8=furniture, 10=price
          ├── 📄 054123456.txt   # Phone in filename, ad text in content
          ├── 🖼️ photo1.jpg     # Up to 5 images
          └── 🖼️ photo2.jpg
```

## ⏰ **Processing Time Estimates**

| Configuration | Time per Ad | 5 Ads | 10 Ads |
|--------------|-------------|-------|--------|
| Fast Mode | 2-3 min | 10-15 min | 20-30 min |
| Balanced | 6-7 min | 30-35 min | 60-70 min |
| Maximum Security | 8-10 min | 40-50 min | 80-100 min |

## 🚨 **Common Issues & Quick Fixes**

| Issue | Quick Fix |
|-------|-----------|
| `❌ Login failed` | Check `ORBITA_LOGIN_EMAIL` and `ORBITA_LOGIN_PASSWORD` |
| `❌ reCAPTCHA failed` | Check `CAPTCHA_API_KEY` and 2captcha balance |
| `❌ No folders found` | Check Google Drive folder structure |
| `❌ Tor connection timeout` | Increase `TOR_STARTUP_DELAY = 20` |
| `❌ Element not found` | Increase `BROWSER_SLOW_MO = 3000` |

## 🧪 **Testing Workflow**

1. **First Time Setup:**
   ```bash
   python test_tor_improved.py        # Test Tor
   python test_ip_comparison.py       # Verify IP anonymization
   ```

2. **Before Production Run:**
   ```bash
   # Test with 1-2 ads first
   python orbita_form_filler.py
   ```

3. **Monitor Success:**
   - Check console logs for ✅/❌ indicators
   - Verify `processed_ads.log` for completed ads
   - Monitor IP changes in logs

## 🔧 **Troubleshooting Commands**

```bash
# Reset Google Drive authorization
rm token.json

# Check Tor is working
python -c "from orbita_form_filler import TorIPChanger; t=TorIPChanger(); t.initialize_tor(); t.start_tor(); print('IP:', t.get_current_ip())"

# Test 2captcha balance
python -c "from twocaptcha import TwoCaptcha; solver = TwoCaptcha('your_api_key'); print('Balance:', solver.balance())"
```

## 📊 **Status Indicators**

| Symbol | Meaning |
|--------|---------|
| ✅ | Success |
| ❌ | Error/Failure |
| ⏳ | Waiting/Processing |
| 🔄 | IP Changing |
| 🔐 | Authentication |
| 🤖 | reCAPTCHA |
| 📝 | Form Filling |
| 🌐 | Network/Tor |

---

**💡 Tip**: Start with **Balanced Security** settings and adjust based on your needs! 