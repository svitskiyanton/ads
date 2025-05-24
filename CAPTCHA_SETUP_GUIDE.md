# 🤖 reCAPTCHA Bypass Setup Guide

This guide explains how to set up automatic reCAPTCHA solving for the Orbita form filler.

## 📋 Prerequisites

1. **2captcha Account**: Sign up at [2captcha.com](https://2captcha.com/)
2. **API Key**: Get your API key from your 2captcha dashboard
3. **Account Balance**: Ensure you have sufficient balance (reCAPTCHA v2 costs ~$0.001 per solve)

## 🔧 Setup Steps

### 1. Install Required Library
```bash
pip install 2captcha-python
```

### 2. Configure API Key

Edit the `config.py` file and replace `YOUR_API_KEY_HERE` with your actual 2captcha API key:

```python
# config.py
CAPTCHA_API_KEY = "your_actual_2captcha_api_key_here"
```

### 3. Test Configuration

Run this test to verify your setup:

```python
from twocaptcha import TwoCaptcha

# Test your API key
api_key = "your_api_key_here"
solver = TwoCaptcha(api_key)

try:
    balance = solver.balance()
    print(f"✅ 2captcha connection successful!")
    print(f"💰 Account balance: ${balance}")
except Exception as e:
    print(f"❌ Error: {e}")
```

## 🤖 How It Works

### Detection
The script automatically detects reCAPTCHA using multiple selectors:
- `#rc-anchor-container` - Main reCAPTCHA container
- `.g-recaptcha` - Standard reCAPTCHA class
- `.recaptcha-checkbox` - Checkbox element
- `iframe[src*="recaptcha"]` - reCAPTCHA iframe

### Solving Process
1. **Extract Site Key**: Finds the reCAPTCHA site key from the page
2. **Submit to 2captcha**: Sends the site key and page URL to 2captcha
3. **Wait for Solution**: 2captcha workers solve the CAPTCHA (usually 10-60 seconds)
4. **Inject Response**: The solution token is injected into the page
5. **Verify**: Checks if the reCAPTCHA is now marked as solved

### Response Injection
The script uses multiple methods to inject the CAPTCHA response:
- Sets `g-recaptcha-response` textarea value
- Updates hidden input fields
- Triggers change events for page validation
- Attempts to interact with Google's reCAPTCHA API

## 💰 Pricing

- **reCAPTCHA v2**: ~$0.001 per solve
- **reCAPTCHA v3**: ~$0.002 per solve
- **Bulk discounts**: Available for high volume

## ⚡ Performance

- **Success Rate**: 95-99% for reCAPTCHA v2
- **Average Solve Time**: 15-45 seconds
- **Failed Attempts**: Automatically retried (charged only on success)

## 🛡️ Anti-Detection Features

The script includes several anti-detection measures:

### Browser Fingerprinting
- Custom user agent
- Hidden automation properties
- Mock navigator properties
- Realistic viewport size

### Behavioral Mimicking
- Slow motion actions (2-second delays)
- Human-like typing patterns
- Random delays between actions
- Natural mouse movements

### Network Headers
- Standard browser headers
- Accept-Language settings
- Connection keep-alive
- DNT (Do Not Track) header

## 🐛 Troubleshooting

### Common Issues

**❌ API Key Invalid**
```
Error: ERROR_KEY_DOES_NOT_EXIST
```
- Check your API key is correct
- Verify account is active
- Ensure sufficient balance

**❌ Site Key Not Found**
```
Could not find reCAPTCHA site key
```
- reCAPTCHA may not be loaded yet
- Check page selectors
- Wait longer for page to load

**❌ Solution Injection Failed**
```
reCAPTCHA response injected but verification unclear
```
- Page may use custom validation
- Try submitting form anyway
- Check browser console for errors

### Debug Mode

Enable debug logging in `config.py`:
```python
DEBUG_CONSOLE_LOGS = True
DEBUG_SCREENSHOTS = True
```

This will:
- Show detailed console output
- Take screenshots at key steps
- Log JavaScript execution

## 🔄 Alternative Services

If 2captcha doesn't work well, you can integrate other services:

### Anti-Captcha
```python
# Alternative implementation
from anticaptchaofficial.recaptchav2proxyless import *

def solve_with_anticaptcha(site_key, page_url):
    solver = recaptchaV2Proxyless()
    solver.set_key("your_anticaptcha_key")
    solver.set_website_url(page_url)
    solver.set_website_key(site_key)
    return solver.solve_and_return_solution()
```

### CapSolver
```python
# Alternative implementation  
import capsolver

def solve_with_capsolver(site_key, page_url):
    capsolver.api_key = "your_capsolver_key"
    solution = capsolver.solve({
        "type": "ReCaptchaV2TaskProxyless",
        "websiteURL": page_url,
        "websiteKey": site_key
    })
    return solution['gRecaptchaResponse']
```

## ⚖️ Legal and Ethical Considerations

- **Use Responsibly**: Only use for legitimate automation purposes
- **Respect Terms**: Check website terms of service
- **Rate Limiting**: Don't overwhelm servers with requests
- **Privacy**: Ensure compliance with data protection laws

## 📊 Success Monitoring

The script tracks reCAPTCHA solving statistics:
- Detection rate
- Solve success rate
- Average solve time
- Failed attempts

Monitor your logs to optimize performance and troubleshoot issues.

## 🚀 Advanced Configuration

For high-volume operations, consider:

### Multiple API Keys
```python
# Rotate between multiple accounts
CAPTCHA_API_KEYS = [
    "key1_for_backup",
    "key2_for_load_balancing", 
    "key3_for_redundancy"
]
```

### Custom Timeouts
```python
# Adjust timeouts for your needs
CAPTCHA_TIMEOUT = 120  # 2 minutes max wait
CAPTCHA_POLLING_INTERVAL = 5  # Check every 5 seconds
```

### Proxy Integration
```python
# Use proxies to avoid IP blocks
PROXY_LIST = [
    "http://proxy1:port",
    "http://proxy2:port"
]
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review 2captcha documentation
3. Test with their online demo
4. Contact 2captcha support for API issues

---

**Remember**: reCAPTCHA solving costs money, so test thoroughly with small batches before running large-scale operations! 💡 