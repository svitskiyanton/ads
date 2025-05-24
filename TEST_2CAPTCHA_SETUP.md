# 2captcha Test Setup Guide

This is a simplified test script to verify 2captcha integration before implementing it in the main ad posting system.

## Prerequisites

1. **2captcha Account**: Sign up at https://2captcha.com/
2. **API Key**: Get your API key from the 2captcha dashboard
3. **Playwright**: Already installed if you set up the main script

## Setup Steps

### 1. Install Dependencies (if not already done)
```bash
pip install -r requirements_test.txt
```

### 2. Install Playwright Browsers (if not already done)
```bash
playwright install
```

### 3. Get 2captcha API Key
1. Go to https://2captcha.com/
2. Register an account
3. Add funds to your account (minimum $3 for testing)
4. Go to your account settings and copy your API key

## Running the Test

1. Run the script:
```bash
python test_2captcha_orbita.py
```

2. When prompted, enter your 2captcha API key

3. The script will:
   - Open the Orbita form page
   - Select "Отдых" from the board dropdown
   - Fill the ad text with "Отдохну"
   - Fill the email with "111@gmail.com"
   - Check the terms agreement checkbox
   - Solve the reCAPTCHA using 2captcha service
   - Submit the form

## What the Script Tests

- **Form Detection**: Finds and fills form fields correctly
- **Board Selection**: Selects the correct category
- **Captcha Integration**: Tests 2captcha API integration
- **Form Submission**: Verifies the complete workflow

## Cost

- Each reCAPTCHA solve costs approximately $0.002-0.003
- Test runs should cost less than $0.01 each

## Expected Behavior

1. Browser opens and navigates to the form
2. Form fields are filled automatically
3. Script waits for captcha to be solved (10-60 seconds)
4. Form is submitted
5. You should see success message or be redirected

## Troubleshooting

- **"Could not find reCAPTCHA site key"**: The page structure may have changed
- **"Timeout waiting for captcha solution"**: 2captcha service may be slow, try again
- **"Failed to submit captcha"**: Check your API key and account balance
- **Form fields not filled**: HTML structure may have changed, script will log warnings

## Next Steps

Once this test works correctly, the same 2captcha integration will be added to the main `orbita_form_filler.py` script for automated bulk ad posting. 