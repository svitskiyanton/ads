#!/usr/bin/env python3
"""
Test script for posting ads on Orbita.co.il after authentication
Steps:
1. Login with provided credentials
2. Navigate to ad posting page
3. Fill form and solve captcha
4. Submit and check result
"""

import asyncio
from playwright.async_api import async_playwright
import logging
from config import CAPTCHA_API_KEY
from twocaptcha import TwoCaptcha

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuthenticatedAdPoster:
    def __init__(self):
        self.login_email = "dadedex420@leabro.com"
        self.login_password = "A)(S*DASdjkl232asjdasd"
        
    async def login(self, page):
        """Login to Orbita account"""
        logger.info("🔐 Starting login process...")
        
        # Go to login page
        await page.goto("https://passport.orbita.co.il/site/login")
        await page.wait_for_load_state('networkidle')
        
        # Fill login form
        await page.fill('#loginform-email', self.login_email)
        await page.fill('#loginform-password', self.login_password)
        
        logger.info("📧 Credentials filled, submitting login...")
        
        # Submit login form
        await page.click('button[name="login-button"]')
        
        # Wait for login to complete
        await page.wait_for_timeout(3000)
        
        # Check if login was successful
        current_url = page.url
        if "passport.orbita.co.il/site/login" not in current_url:
            logger.info(f"✅ Login successful! Redirected to: {current_url}")
            return True
        else:
            # Check for error messages
            error_elements = await page.locator('.alert, .error, .invalid-feedback').all()
            if error_elements:
                for element in error_elements:
                    error_text = await element.text_content()
                    if error_text and error_text.strip():
                        logger.error(f"❌ Login error: {error_text}")
            logger.error("❌ Login failed - still on login page")
            return False
    
    async def post_test_ad(self, page):
        """Post test ad after successful login"""
        logger.info("📝 Navigating to ad posting page...")
        
        # Navigate to ad posting page
        await page.goto("https://doska.orbita.co.il/my/add/")
        await page.wait_for_load_state('networkidle')
        
        # Verify we're on the right page
        if "my/add" not in page.url:
            logger.error(f"❌ Unexpected redirect to: {page.url}")
            return False
        
        logger.info("✅ On ad posting page, filling form...")
        
        # Add human-like delays
        await page.wait_for_timeout(2000)
        
        try:
            # Select board
            logger.info("🔘 Selecting board...")
            await page.select_option('select[name="board"]', label="Отдых")
            await page.wait_for_timeout(1000)
            logger.info("✅ Board selected")
            
            # Select city (required field)
            logger.info("🏙️ Selecting city...")
            city_select = page.locator('select[name="city"]')
            if await city_select.count() > 0:
                # Try to select a specific city first, fallback to "Весь Израиль"
                try:
                    await page.select_option('select[name="city"]', label="Тель-Авив")
                    logger.info("✅ City selected: Тель-Авив")
                except:
                    try:
                        await page.select_option('select[name="city"]', label="Весь Израиль")
                        logger.info("✅ City selected: Весь Израиль")
                    except:
                        logger.warning("⚠️ Could not select city")
            else:
                logger.warning("⚠️ City select not found")
            
            await page.wait_for_timeout(1000)
            
            # Fill text content
            logger.info("📝 Filling text content...")
            textareas = await page.locator('textarea[name="info"]').all()
            if textareas:
                await textareas[0].fill("Отдых")
                await page.wait_for_timeout(1000)
                logger.info("✅ Text content filled")
            else:
                logger.warning("⚠️ No textarea found")
            
            # Check if email field exists and is required (after login it might not be)
            logger.info("📧 Checking email field...")
            email_input = page.locator('input[name="email"]')
            email_count = await email_input.count()
            
            if email_count > 0:
                # Check if it's visible and editable
                is_visible = await email_input.is_visible()
                is_enabled = await email_input.is_enabled()
                current_value = await email_input.input_value()
                
                logger.info(f"📧 Email field - Visible: {is_visible}, Enabled: {is_enabled}, Current value: '{current_value}'")
                
                if is_visible and is_enabled and not current_value:
                    await page.fill('input[name="email"]', "111@gmail.com")
                    logger.info("✅ Email filled")
                else:
                    logger.info("ℹ️ Email field not filled (already has value or not editable)")
            else:
                logger.info("ℹ️ No email field found (normal after login)")
            
            await page.wait_for_timeout(1000)
            
            # Check terms
            logger.info("☑️ Checking terms...")
            terms_checkbox = page.locator('input[name="terms"]')
            if await terms_checkbox.count() > 0:
                await page.check('input[name="terms"]')
                logger.info("✅ Terms checked")
            else:
                logger.warning("⚠️ Terms checkbox not found")
            
            await page.wait_for_timeout(1000)
            
            # Solve captcha
            logger.info("🤖 Solving reCAPTCHA...")
            captcha_solved = await self.solve_captcha(page)
            
            if not captcha_solved:
                logger.error("❌ Failed to solve captcha")
                return False
            
            logger.info("✅ Form filled, submitting...")
            
            # Submit form
            submit_button = page.locator('#submit_but')
            if await submit_button.count() > 0:
                await page.click('#submit_but')
                logger.info("✅ Submit button clicked")
            else:
                logger.error("❌ Submit button not found")
                return False
            
            # Wait for response
            await page.wait_for_timeout(5000)
            
            # Check result
            final_url = page.url
            logger.info(f"📍 Final URL: {final_url}")
            
            if "passport.orbita.co.il/site/login" in final_url:
                logger.error("❌ Redirected to login - authentication issue persists")
                return False
            elif "addsuccess=1" in final_url:
                logger.info("🎉 SUCCESS! Ad posted successfully!")
                return True
            elif "my/add" in final_url:
                # Detailed error analysis
                logger.info("🔍 Analyzing validation errors...")
                
                # Check for various error message selectors
                error_selectors = [
                    '.alert-danger',
                    '.alert-warning', 
                    '.error',
                    '.help-block',
                    '.invalid-feedback',
                    '.field-error',
                    '.validation-error',
                    '.text-danger',
                    '[style*="color: red"]',
                    '[style*="color:#red"]'
                ]
                
                errors_found = []
                for selector in error_selectors:
                    error_elements = await page.locator(selector).all()
                    for element in error_elements:
                        error_text = await element.text_content()
                        if error_text and error_text.strip():
                            errors_found.append(f"{selector}: {error_text.strip()}")
                
                if errors_found:
                    logger.error("❌ Validation errors found:")
                    for error in errors_found:
                        logger.error(f"   {error}")
                else:
                    logger.info("🔍 No obvious error messages found. Checking form state...")
                    
                    # Check form field values
                    form_state = await page.evaluate("""
                        () => {
                            const form = document.querySelector('form');
                            if (!form) return {error: 'No form found'};
                            
                            const formData = new FormData(form);
                            const data = {};
                            for (let [key, value] of formData.entries()) {
                                data[key] = value;
                            }
                            
                            // Also check for required fields
                            const requiredFields = [];
                            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
                            inputs.forEach(input => {
                                requiredFields.push({
                                    name: input.name || input.id,
                                    type: input.type || input.tagName,
                                    value: input.value,
                                    required: input.required
                                });
                            });
                            
                            return {formData: data, requiredFields: requiredFields};
                        }
                    """)
                    
                    logger.info(f"📋 Form state: {form_state}")
                
                logger.warning("⚠️ Still on form page - submission rejected")
                return False
            else:
                logger.info(f"🤔 Unexpected final page: {final_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during form filling: {e}")
            # Take a screenshot for debugging
            try:
                await page.screenshot(path="error_screenshot.png")
                logger.info("📸 Error screenshot saved as error_screenshot.png")
            except:
                pass
            return False
    
    async def solve_captcha(self, page):
        """Solve reCAPTCHA using 2captcha service"""
        try:
            # Find captcha site key
            site_key = await page.get_attribute('[data-sitekey]', 'data-sitekey')
            if not site_key:
                logger.error("❌ No reCAPTCHA site key found")
                return False
            
            logger.info(f"🔑 Found site key: {site_key}")
            
            # Solve with 2captcha
            solver = TwoCaptcha(CAPTCHA_API_KEY)
            result = solver.recaptcha(sitekey=site_key, url=page.url, version='v2')
            
            if result and 'code' in result:
                logger.info("🔧 Injecting captcha solution...")
                
                # Inject solution with more thorough method
                success = await page.evaluate(f"""
                    () => {{
                        try {{
                            // Set the response in the hidden textarea
                            const responseTextarea = document.getElementById('g-recaptcha-response');
                            if (responseTextarea) {{
                                responseTextarea.value = '{result['code']}';
                                responseTextarea.style.display = 'block';
                            }}
                            
                            // Try to trigger the callback if it exists
                            if (typeof grecaptcha !== 'undefined') {{
                                const widgets = document.querySelectorAll('[data-sitekey]');
                                widgets.forEach(widget => {{
                                    const widgetId = widget.getAttribute('data-widget-id');
                                    if (widgetId) {{
                                        try {{
                                            grecaptcha.execute(widgetId);
                                        }} catch(e) {{
                                            console.log('Execute failed:', e);
                                        }}
                                    }}
                                }});
                            }}
                            
                            // Also set in any other captcha response fields
                            const allCaptchaInputs = document.querySelectorAll('textarea[name="g-recaptcha-response"]');
                            allCaptchaInputs.forEach(input => {{
                                input.value = '{result['code']}';
                            }});
                            
                            return true;
                        }} catch(error) {{
                            console.error('Captcha injection error:', error);
                            return false;
                        }}
                    }}
                """)
                
                if success:
                    logger.info("✅ reCAPTCHA solution injected successfully")
                    
                    # Wait a bit for the captcha to be processed
                    await page.wait_for_timeout(2000)
                    
                    # Verify the solution was accepted
                    response_value = await page.evaluate("""
                        () => {
                            const textarea = document.getElementById('g-recaptcha-response');
                            return textarea ? textarea.value : '';
                        }
                    """)
                    
                    if response_value:
                        logger.info(f"✅ Captcha response verified: {response_value[:50]}...")
                        return True
                    else:
                        logger.error("❌ Captcha response not found after injection")
                        return False
                else:
                    logger.error("❌ Failed to inject captcha solution")
                    return False
            else:
                logger.error("❌ Failed to get captcha solution from 2captcha")
                return False
                
        except Exception as e:
            logger.error(f"❌ Captcha solving error: {e}")
            return False
    
    async def run_test(self):
        """Run the complete authenticated posting test"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                # Step 1: Login
                login_success = await self.login(page)
                if not login_success:
                    logger.error("❌ Cannot proceed - login failed")
                    return
                
                # Wait a few seconds as requested
                logger.info("⏳ Waiting a few seconds before proceeding...")
                await page.wait_for_timeout(3000)
                
                # Step 2: Post test ad
                post_success = await self.post_test_ad(page)
                
                if post_success:
                    logger.info("🎉 COMPLETE SUCCESS! Authenticated ad posting works!")
                else:
                    logger.info("❌ Ad posting failed even with authentication")
                
                logger.info("🔍 Keeping browser open for inspection...")
                input("Press ENTER to close browser...")
                
            except Exception as e:
                logger.error(f"❌ Test error: {e}")
            finally:
                await browser.close()

async def main():
    if not CAPTCHA_API_KEY or CAPTCHA_API_KEY == "YOUR_API_KEY_HERE":
        logger.error("Please set your 2captcha API key in config.py!")
        return
    
    poster = AuthenticatedAdPoster()
    await poster.run_test()

if __name__ == "__main__":
    asyncio.run(main()) 