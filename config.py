# Configuration file for Orbita Form Filler

# 2captcha API Configuration
# Get your API key from: https://2captcha.com/enterpage
# Replace 'YOUR_API_KEY_HERE' with your actual 2captcha API key
CAPTCHA_API_KEY = "1b0bad4aff52861dae002c642c027c51"  # ← Put your API key here

# Orbita.co.il Account Credentials (required for ad posting)
# Replace with your actual account credentials
ORBITA_LOGIN_EMAIL = "dadedex420@leabro.com"
ORBITA_LOGIN_PASSWORD = "A)(S*DASdjkl232asjdasd"

# Alternative CAPTCHA services (for future implementation)
# ANTICAPTCHA_API_KEY = "YOUR_ANTICAPTCHA_API_KEY"
# CAPSOLVER_API_KEY = "YOUR_CAPSOLVER_API_KEY"

# Browser settings
BROWSER_HEADLESS = False
BROWSER_SLOW_MO = 2000  # Milliseconds between actions

# Form filling delays (in seconds)
STEP_DELAY = 2
RECAPTCHA_WAIT = 3
FORM_LOAD_WAIT = 3

# Google Drive settings
GOOGLE_DRIVE_PARENT_FOLDER = "ad"

# Debug settings
DEBUG_SCREENSHOTS = False
DEBUG_CONSOLE_LOGS = True 