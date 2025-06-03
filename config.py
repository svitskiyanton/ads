# Configuration file for Orbita Form Filler

# ============================================================================
# REQUIRED CONFIGURATION - MUST BE SET BEFORE RUNNING
# ============================================================================

# 2captcha API Configuration (REQUIRED)
# Get your API key from: https://2captcha.com/
CAPTCHA_API_KEY = ""

# OpenAI API Configuration (REQUIRED for new algorithm)
# Get your API key from: https://platform.openai.com/
OPENAI_API_KEY = ""

# ============================================================================
# BROWSER SETTINGS
# ============================================================================

# Browser behavior
BROWSER_HEADLESS = False        # True = hidden browser, False = visible browser
BROWSER_SLOW_MO = 2000         # Milliseconds between actions (1000-3000 recommended)

# Form filling delays (in seconds)
STEP_DELAY = 2                 # General delay between form steps
RECAPTCHA_WAIT = 3             # Wait time for reCAPTCHA to load
FORM_LOAD_WAIT = 3             # Wait time for form to load completely

# ============================================================================
# TOR IP ROTATION SETTINGS
# ============================================================================

USE_TOR_IP_ROTATION = True     # Enable/disable Tor IP rotation for anonymity
TOR_IP_CHANGE_INTERVAL = 3     # Change IP every N ads (0 = disabled)
TOR_STARTUP_DELAY = 15         # Seconds to wait after starting Tor
TOR_IP_CHANGE_DELAY = 5        # Seconds to wait after changing IP

# ============================================================================
# ENHANCED SECURITY WORKFLOW
# ============================================================================

LOGOUT_BETWEEN_ADS = False     # Changed: No logout between ads, only after last ad
WAIT_AFTER_LOGOUT = 180        # Wait time in seconds after logout (3 minutes)
CHANGE_IP_AFTER_LOGOUT = True  # Change IP after logout (requires Tor)
WAIT_BETWEEN_ADS = 180         # Wait 3 minutes between ads (unchanged)

# ============================================================================
# GOOGLE DRIVE SETTINGS
# ============================================================================

# Google Drive path structure - FOUND! Using discovered path structure
# Found folder: "Real estate" with subfolder structure intact
GOOGLE_DRIVE_PATH = "Real estate/Ришон Лецион/ПРОДАЖА"  # Complete discovered path
MAX_IMAGES_PER_AD = 5          # Maximum images to upload per ad

# Google Drive API rate limiting
GOOGLE_DRIVE_API_DELAY = 0.5   # Reasonable delay between API calls (seconds)

# Alternative paths for testing:
# GOOGLE_DRIVE_PATH = "Real estate"  # Just the main folder
# GOOGLE_DRIVE_PATH = "ad"  # Alternative English folder

# ============================================================================
# REGISTRATION SETTINGS (NEW ALGORITHM)
# ============================================================================

# Auto-registration settings for new accounts
# NOTE: Each run creates a fresh account with random email
AUTO_REGISTER_ACCOUNTS = True
REGISTRATION_PASSWORD = "S()d8f0sdfuios23434"  # Fixed password for all accounts
REGISTRATION_NAME = "Konstantin"               # Fixed name for all accounts

# ============================================================================
# DEBUG SETTINGS
# ============================================================================

DEBUG_SCREENSHOTS = False     # Take screenshots for debugging
DEBUG_CONSOLE_LOGS = True     # Show detailed console logs

# Additional settings
# Add any additional settings you need here

# End of configuration file 