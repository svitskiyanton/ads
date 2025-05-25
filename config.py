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

# Tor IP Changing settings
USE_TOR_IP_ROTATION = True  # Enable/disable Tor IP rotation
TOR_IP_CHANGE_INTERVAL = 3  # Change IP every N ads (set to 1 for every ad, 0 to disable)
TOR_STARTUP_DELAY = 15      # Seconds to wait after starting Tor (increased for better circuit establishment)
TOR_IP_CHANGE_DELAY = 5     # Seconds to wait after changing IP (increased)

# Enhanced security workflow settings
LOGOUT_BETWEEN_ADS = True   # Logout after each ad for better security
WAIT_AFTER_LOGOUT = 180     # Wait time in seconds after logout (3 minutes = 180 seconds)
CHANGE_IP_AFTER_LOGOUT = True  # Change IP after logout (requires Tor)

# Additional settings
# Add any additional settings you need here

# End of configuration file 