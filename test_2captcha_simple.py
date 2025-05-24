#!/usr/bin/env python3
"""
Simplified test script to compare manual vs automated form filling
Avoids localStorage issues and focuses on essential debugging
"""

import asyncio
import time
from playwright.async_api import async_playwright
import logging
from config import CAPTCHA_API_KEY
from twocaptcha import TwoCaptcha
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleFormAnalyzer:
    """Simple form analyzer without complex monitoring"""
    
    def __init__(self, captcha_api_key):
        self.captcha_api_key = captcha_api_key
        self.site_url = "https://doska.orbita.co.il/my/add/"
        
    async def capture_form_data(self, page, label):
        """Capture just the essential form data"""
        try:
            form_data = await page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    const result = [];
                    
                    forms.forEach((form, index) => {
                        const formData = new FormData(form);
                        const data = {};
                        
                        // Get all form data
                        for (let [key, value] of formData.entries()) {
                            data[key] = value.toString();
                        }
                        
                        result.push({
                            index: index,
                            action: form.action,
                            method: form.method,
                            data: data
                        });
                    });
                    
                    return {
                        url: window.location.href,
                        title: document.title,
                        forms: result
                    };
                }
            """)
            
            # Save to file
            os.makedirs("simple_debug", exist_ok=True)
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"simple_debug/{label}_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(form_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Saved form data: {filename}")
            
            # Log summary
            for form in form_data['forms']:
                logger.info(f"Form {form['index']}: {len(form['data'])} fields")
                for key, value in form['data'].items():
                    if len(str(value)) > 50:
                        logger.info(f"  {key}: {str(value)[:50]}...")
                    else:
                        logger.info(f"  {key}: {value}")
            
            return form_data
            
        except Exception as e:
            logger.error(f"Error capturing form data: {e}")
            return None
    
    async def manual_test(self):
        """Simple manual test - just open browser and wait"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                logger.info("🔍 MANUAL TEST MODE")
                logger.info("Fill the form manually, then press ENTER in this console when done")
                
                await page.goto(self.site_url)
                await page.wait_for_load_state('networkidle')
                
                # Capture initial state
                await self.capture_form_data(page, "manual_initial")
                
                # Wait for user to fill manually
                input("📝 Fill the form manually, solve captcha, and submit. Then press ENTER here...")
                
                # Capture final state  
                await self.capture_form_data(page, "manual_final")
                
                logger.info("✅ Manual test complete!")
                
            except Exception as e:
                logger.error(f"Manual test error: {e}")
            finally:
                await browser.close()
    
    async def automated_test(self):
        """Simple automated test"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                logger.info("🤖 AUTOMATED TEST MODE")
                
                await page.goto(self.site_url)
                await page.wait_for_load_state('networkidle')
                
                # 🎯 WAIT FOR GOOGLE ANALYTICS REGION CHECK
                logger.info("⏳ Waiting for Google Analytics region check to complete...")
                await page.wait_for_timeout(10000)  # Wait 10 seconds for GA
                
                # Check if GA loaded properly
                ga_status = await page.evaluate("""
                    () => {
                        return {
                            ga_loaded: typeof gtag !== 'undefined' || typeof ga !== 'undefined' || typeof google_tag_manager !== 'undefined',
                            ga_scripts: document.querySelectorAll('script[src*="google-analytics"], script[src*="googletagmanager"]').length,
                            page_ready: document.readyState
                        };
                    }
                """)
                logger.info(f"📊 Google Analytics status: {ga_status}")
                
                # Additional wait if GA is still loading
                if ga_status['ga_scripts'] > 0:
                    logger.info("📊 Detected Google Analytics, waiting longer...")
                    await page.wait_for_timeout(5000)  # Extra 5 seconds
                
                # Capture initial state
                await self.capture_form_data(page, "auto_initial")
                
                # Fill form WITH DELAYS (mimic human behavior)
                logger.info("🐌 Filling form slowly to mimic human behavior...")
                await self._fill_form_human_like(page)
                
                # Capture before captcha
                await self.capture_form_data(page, "auto_before_captcha")
                
                # Solve captcha
                await self._solve_captcha_simple(page)
                
                # Capture after captcha
                await self.capture_form_data(page, "auto_after_captcha")
                
                # Wait before submission (let GA process)
                logger.info("⏳ Waiting before submission for GA to process...")
                await page.wait_for_timeout(3000)
                
                # Submit
                await self._submit_simple(page)
                
                # Wait and capture final
                await page.wait_for_timeout(3000)
                await self.capture_form_data(page, "auto_final")
                
                logger.info("🤖 Automated test complete!")
                
                # Keep browser open to see result
                input("Press ENTER to close browser...")
                
            except Exception as e:
                logger.error(f"Automated test error: {e}")
            finally:
                await browser.close()
    
    async def _fill_form_human_like(self, page):
        """Fill form with human-like delays"""
        # Select board with delay
        try:
            await page.select_option('select[name="board"]', label="Отдых")
            logger.info("✅ Selected board: Отдых")
            await page.wait_for_timeout(2000)  # Human-like delay
        except:
            logger.warning("❌ Could not select board")
        
        # Fill ad text with delay
        try:
            textareas = await page.locator('textarea[name="info"]').all()
            if textareas:
                await textareas[0].fill("Отдохну")
                logger.info("✅ Filled ad text")
                await page.wait_for_timeout(1500)  # Human-like delay
        except:
            logger.warning("❌ Could not fill ad text")
        
        # Fill email with delay
        try:
            await page.fill('input[name="email"]', "111@gmail.com")
            logger.info("✅ Filled email")
            await page.wait_for_timeout(1000)  # Human-like delay
        except:
            try:
                textareas = await page.locator('textarea[name="info"]').all()
                if len(textareas) > 1:
                    await textareas[1].fill("111@gmail.com")
                    logger.info("✅ Filled email in textarea")
                    await page.wait_for_timeout(1000)
            except:
                logger.warning("❌ Could not fill email")
        
        # Check terms with delay
        try:
            await page.check('input[name="terms"]')
            logger.info("✅ Checked terms")
            await page.wait_for_timeout(1000)  # Human-like delay
        except:
            logger.warning("❌ Could not check terms")
    
    async def _solve_captcha_simple(self, page):
        """Simple captcha solving"""
        try:
            # Find site key
            site_key = await page.get_attribute('[data-sitekey]', 'data-sitekey')
            if not site_key:
                raise Exception("No site key found")
            
            logger.info(f"🔑 Site key: {site_key[:20]}...")
            
            # Solve with 2captcha
            solver = TwoCaptcha(self.captcha_api_key)
            result = solver.recaptcha(sitekey=site_key, url=page.url, version='v2')
            
            if result and 'code' in result:
                # Inject response
                await page.evaluate(f"""
                    document.getElementById('g-recaptcha-response').value = '{result['code']}';
                """)
                logger.info("✅ Captcha solved and injected")
            else:
                raise Exception("Captcha solving failed")
                
        except Exception as e:
            logger.error(f"❌ Captcha error: {e}")
    
    async def _submit_simple(self, page):
        """Simple form submission"""
        try:
            await page.click('#submit_but')
            logger.info("✅ Clicked submit")
        except:
            try:
                await page.click('input[name="add_message"]')
                logger.info("✅ Clicked submit (alternative)")
            except:
                logger.warning("❌ Could not find submit button")

async def main():
    if not CAPTCHA_API_KEY or CAPTCHA_API_KEY == "YOUR_API_KEY_HERE":
        logger.error("Please set your 2captcha API key in config.py!")
        return
    
    analyzer = SimpleFormAnalyzer(CAPTCHA_API_KEY)
    
    print("\n🎯 Choose test mode:")
    print("1. Manual test (you fill form)")
    print("2. Automated test (script fills form)")
    choice = input("Enter choice (1 or 2): ").strip()
    
    try:
        if choice == "1":
            await analyzer.manual_test()
        else:
            await analyzer.automated_test()
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 